import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "harnoisenergies.com"
    start_url = "https://harnoisenergies.com/en/find-service-station/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = (
        '{"stores'
        + dom.xpath('//script[contains(text(), "MXOStoreLocatorComponent")]/text()')[0]
        .split("    );\n    mxoStore")[0]
        .split('{"stores')[-1]
    )
    data = json.loads(data)
    for store_number, poi in data["stores"].items():
        location_type = poi["brand"]
        if location_type != "Pétro-T":
            continue

        item = SgRecord(
            locator_domain=domain,
            page_url=poi["landingPageUrl"],
            location_name=poi["title"],
            street_address=poi["location"]["address1"],
            city=poi["location"]["city"],
            state=poi["location"]["state"],
            zip_postal=poi["location"]["zip"],
            country_code="",
            store_number=store_number,
            phone="",
            location_type=location_type,
            latitude=poi["location"]["coordinates"]["latitude"],
            longitude=poi["location"]["coordinates"]["longitude"],
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
