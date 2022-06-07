# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "http://www.italiancoffee.com/obtener_ciudades.php"
    domain = "italiancoffee.com"
    hdr = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    data = session.post(start_url, headers=hdr).json()

    for city in data["México"]["cities"].keys():
        all_stores = data["México"]["cities"][city]["stores"]
        for location_name, poi in all_stores.items():

            item = SgRecord(
                locator_domain=domain,
                page_url="http://www.italiancoffee.com/ubicaciones.php",
                location_name=location_name,
                street_address=poi["address"],
                city=city,
                state="",
                zip_postal="",
                country_code="México",
                store_number="",
                phone=poi["phone"],
                location_type="",
                latitude=poi["lat"],
                longitude=poi["lng"],
                hours_of_operation="",
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
