import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "christianlouboutin.com"
    start_url = "https://eu.christianlouboutin.com/uk_en/storelocator/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = (
        dom.xpath('//script[contains(text(), "LocatorData   =")]/text()')[0]
        .split("LocatorData   =")[1]
        .split(";\n    window")[0]
    )
    data = json.loads(data)

    for poi in data["retailers"]:
        hoo = []
        for e in poi["schedule_data"]:
            hoo.append(f'{e["day"]}: {e["label"]}')
        hoo = ", ".join(hoo)
        zip_code = poi["zipcode"]
        street_address = poi["street"]
        if zip_code and zip_code in street_address:
            street_address = street_address.split(",")[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=poi["store_url"],
            location_name=poi["name"],
            street_address=street_address,
            city=poi["city"],
            state="",
            zip_postal=zip_code,
            country_code=poi["country"],
            store_number=poi["retailer_id"],
            phone=poi["phone"],
            location_type="",
            latitude=poi["latitude"],
            longitude=poi["longitude"],
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
