from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.customink.com/ink/stores"
    domain = "customink.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_states = dom.xpath('//div[@class="ip-LocalStores-state "]')
    for state in all_states:
        state_id = state.xpath("@data-state")[0]
        city = state.xpath("@data-location")[0]
        radius = state.xpath("@data-radius")[0]
        state_url = f"https://www.customink.com/ink/api/yext-stores?state={state_id}&city={city}&radius={radius}"
        data = session.get(state_url).json()
        for poi in data["stores"]:
            hoo = []
            for day, hours in poi["hours"].items():
                if day == "holidayHours":
                    continue
                if hours and hours.get("openIntervals"):
                    opens = hours["openIntervals"][0]["start"]
                    closes = hours["openIntervals"][0]["end"]
                    hoo.append(f"{day} {opens} - {closes}")
                else:
                    hoo.append(f"{day} closed")
            hoo = " ".join(hoo)
            street_address = poi["address"]["line1"]
            if poi["address"].get("line2"):
                street_address += ", " + poi["address"]["line2"]

            item = SgRecord(
                locator_domain=domain,
                page_url=poi["landingPageUrl"],
                location_name=poi["address"]["city"],
                street_address=street_address,
                city=poi["address"]["city"],
                state=poi["address"]["region"],
                zip_postal=poi["address"]["postalCode"],
                country_code=poi["address"]["countryCode"],
                store_number="",
                phone=poi["mainPhone"],
                location_type="",
                latitude=poi["geocodedCoordinate"]["latitude"],
                longitude=poi["geocodedCoordinate"]["longitude"],
                hours_of_operation=hoo,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
