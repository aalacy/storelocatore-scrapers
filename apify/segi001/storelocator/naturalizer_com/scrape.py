# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from lxml import etree
from time import sleep

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    start_url = "https://www.naturalizer.com/stores"
    domain = "naturalizer.com"

    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(10)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath("//store-details-view")[:-1]
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h5/text()")[0]
        street_address = poi_html.xpath(
            './/span[@data-bind="text: addressText"]/text()'
        )[0]
        city = poi_html.xpath('.//span[@data-bind="text: cityText"]/text()')[0].split(
            ", "
        )[0]
        state = poi_html.xpath('.//span[@data-bind="text: cityText"]/text()')[0].split(
            ", "
        )[-1]
        zip_code = poi_html.xpath(
            './/span[@data-bind="text: formatZip(zipCodeText)"]/text()'
        )[0]
        phone = poi_html.xpath(
            './/span[@data-bind="text: formatPhoneNumber(phoneText)"]/text()'
        )[0]
        hoo = poi_html.xpath('.//div[@class="StoreListResult_hours"]//text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
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
