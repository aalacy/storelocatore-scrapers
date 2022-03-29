import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    domain = "totalaccessurgentcare.com"
    start_url = "https://www.totalaccessurgentcare.com/locations/"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }
    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)
    data = (
        dom.xpath('//script[contains(text(), "tauc_location_object")]/text()')[0]
        .split("object =")[-1]
        .split(";\n/*")[0]
    )
    data = json.loads(data)

    all_locations = json.loads(data["locations_data"])
    for poi in all_locations:
        raw_address = poi["address"]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2

        item = SgRecord(
            locator_domain=domain,
            page_url=urljoin(start_url, poi["slug"]),
            location_name=poi["name"],
            street_address=street_address,
            city=addr.city,
            state=poi["state"],
            zip_postal=addr.postcode,
            country_code="",
            store_number=poi["id"],
            phone=poi["phone"],
            location_type="",
            latitude=poi["latitude"],
            longitude=poi["longitude"],
            hours_of_operation=poi["all_day_timing"],
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
