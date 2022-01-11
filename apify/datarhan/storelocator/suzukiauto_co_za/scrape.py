from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    start_url = "https://www.suzukiauto.co.za/dealers"
    domain = "suzukiauto.co.za"

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath(
        '//div[@class="map-wrapper"]//a[@class="card-wrapper"]/@href'
    )
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = " ".join(loc_dom.xpath("//h1//text()"))
        raw_address = loc_dom.xpath(
            '//div[p[contains(text(), "Address")]]/p[1]/text()'
        )[0].strip()
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        phone = (
            loc_dom.xpath('//div[p[contains(text(), "Give us a call")]]/p[1]//text()')[
                0
            ]
            .split(";")[0]
            .split(":")[-1]
            .strip()
        )
        hoo = loc_dom.xpath('//div[p[contains(text(), "Sales Hours")]]/p/text()')[:-1]
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        if not hoo:
            continue

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state="",
            zip_postal=addr.postcode,
            country_code="ZA",
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation=hoo,
            raw_address=raw_address,
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
