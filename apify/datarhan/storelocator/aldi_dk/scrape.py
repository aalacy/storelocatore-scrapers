import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)
    start_url = "https://find-aldi.dk/t/static/data.js?ver=5.5.5"
    domain = "find-aldi.dk"
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,ru-RU;q=0.8,ru;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
    }

    response = session.get(start_url, headers=hdr)
    data = response.text.split("data =")[-1][:-1]
    all_locations = json.loads(data)
    for poi in all_locations:
        hoo = f'M-F {poi["Open_week"]} Sat {poi["Open_sat"]} Sun {poi["Open_sun"]}'

        item = SgRecord(
            locator_domain=domain,
            page_url="https://find-aldi.dk/",
            location_name=poi["Butiksnavn"],
            street_address=poi["Adress"],
            city=poi["City"],
            state=SgRecord.MISSING,
            zip_postal=poi["Zip"],
            country_code="DK",
            store_number=poi["StoreId"],
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=poi["Latitude"],
            longitude=poi["Longitude"],
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
