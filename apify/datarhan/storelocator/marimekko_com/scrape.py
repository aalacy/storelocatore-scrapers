# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.marimekko.com/us_en/storelocator/"
    domain = "marimekko.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = dom.xpath(
        '//script[@type="text/x-magento-init" and contains(text(), "allCountries")]/text()'
    )[0]
    data = json.loads(data)
    for code in data["*"]["Magento_Ui/js/core/app"]["components"][
        "storelocator-search-form"
    ]["allCountries"]:
        frm = {"request": {"filters": {"country": {"value": code["id"]}}}}
        data = session.post(
            "https://www.marimekko.com/us_en/rest/us_en/V1/store-locator/search",
            headers=hdr,
            json=frm,
        ).json()

        all_locations = data["items"]
        for poi in all_locations:
            if poi["store_type"] == 2:
                location_type = "Marimekko store"
            elif poi["store_type"] == 3:
                continue
            else:
                location_type = "Outlet"
            hoo = []
            for e in poi["working_hours"]:
                hoo.append(f'{e["day"]} {e["hours"]}')
            hoo = " ".join(hoo)
            zip_code = poi["postcode"]
            addr = parse_address_intl(zip_code)
            if "," in zip_code:
                zip_code = addr.postcode
            street_address = poi["street"]
            if not zip_code:
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
            phone = poi.get("phone")
            if phone and len(phone.strip()) == 1:
                phone = ""

            item = SgRecord(
                locator_domain=domain,
                page_url=start_url,
                location_name=poi["name"],
                street_address=street_address,
                city=poi["city"],
                state=poi.get("region"),
                zip_postal=zip_code,
                country_code=poi["country_id"],
                store_number=poi["location_id"],
                phone=phone,
                location_type=location_type,
                latitude=poi["latitude"],
                longitude=poi["longitude"],
                hours_of_operation=hoo,
                raw_address=poi["street"],
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
