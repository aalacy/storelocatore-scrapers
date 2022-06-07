from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    domain = "auto.suzuki.de"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.GERMANY], expected_search_radius_miles=50
    )
    for lat, lng in all_coords:
        frm = {
            "address": "",
            "partner": "",
            "dealertype": "V",
            "count": "10",
            "searchtype": "1",
            "radius": "50",
            "lat": lat,
            "lng": lng,
        }
        all_locations = session.post(
            "https://auto.suzuki.de/dealersearch/search", headers=hdr, data=frm
        ).json()
        for poi in all_locations:
            page_url = poi["dealer"].get("homepage")
            hoo = ""
            if page_url:
                loc_response = session.get(page_url)
                loc_dom = etree.HTML(loc_response.text)
                hoo = loc_dom.xpath(
                    '//div[@class="col-sm-3 sale-open"]//div[@class="one-day-info"]//text()'
                )
                hoo = " ".join([e.strip() for e in hoo if e.strip()])

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["dealer"]["dealername"],
                street_address=poi["location"]["street"],
                city=poi["location"]["city"],
                state=poi["dealer"].get("province"),
                zip_postal=poi["location"]["zip"],
                country_code="DE",
                store_number=poi["location"]["id"],
                phone=poi["location"]["phone"],
                location_type="",
                latitude=poi["location"]["latitude"],
                longitude=poi["location"]["longitude"],
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
