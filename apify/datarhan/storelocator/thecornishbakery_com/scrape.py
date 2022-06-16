import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://stockist.co/api/v1/u10286/locations/all.js?callback=_stockistAllStoresCallback"
    domain = "thecornishbakery.com"
    response = session.get(start_url)
    data = response.text.split("Callback(")[-1][:-2]

    all_locations = json.loads(data)
    for poi in all_locations:
        street_address = poi["address_line_1"]
        if poi["address_line_2"]:
            street_address += ", " + poi["address_line_2"]

        item = SgRecord(
            locator_domain=domain,
            page_url="https://thecornishbakery.com/pages/locations",
            location_name=poi["name"],
            street_address=street_address,
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["postal_code"],
            country_code=poi["country"],
            store_number=poi["id"],
            phone=poi["phone"],
            location_type="",
            latitude=poi["latitude"],
            longitude=poi["longitude"],
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
