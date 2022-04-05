from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://lafiestamarkets.com/"
    domain = "lafiestamarkets.com"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath(
        '//h6[contains(text(), "Locations")]/following-sibling::div//a/text()'
    )

    for raw_data in all_locations:
        raw_data = raw_data.split(", ")
        if len(raw_data) != 3:
            raw_data += ["<MISSING>", "<MISSING>"]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name="",
            street_address=raw_data[0],
            city=raw_data[1],
            state=raw_data[2].split()[0],
            zip_postal=raw_data[2].split()[-1],
            country_code="",
            store_number="",
            phone="",
            location_type="",
            latitude="",
            longitude="",
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
