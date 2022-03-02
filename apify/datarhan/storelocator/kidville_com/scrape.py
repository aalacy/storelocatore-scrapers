import re
from lxml import etree

from sgselenium import SgFirefox
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    start_url = "https://kidville.com/find-a-location/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//div[@class="state-block"]/h3/a/@href')
    for store_url in all_locations:
        if "wuhan" in store_url:
            continue
        with SgFirefox() as driver:
            driver.get(store_url)
            loc_dom = etree.HTML(driver.page_source)
        location_name = loc_dom.xpath("//title/text()")[0].split("|")[0]
        location_name = location_name if location_name else "<MISSING>"
        if not loc_dom.xpath('//p[i[@class="fa fa-map-marker"]]/text()'):
            continue
        raw_address = loc_dom.xpath('//p[i[@class="fa fa-map-marker"]]/text()')[
            0
        ].split(", ")
        street_address = raw_address[0]
        city = raw_address[1]
        state = raw_address[-1].split()[0]
        if state == "China":
            continue
        zip_code = raw_address[-1].split()[-1]
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number="",
            phone=phone,
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
