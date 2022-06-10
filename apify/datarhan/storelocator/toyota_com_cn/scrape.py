from lxml import etree
from time import sleep

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    start_url = "https://www.gac-toyota.com.cn/buy/shopping/dealer-search"
    domain = "toyota.com.cn"

    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(20)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//div[@class="jspPane"]/dd')
    for poi_html in all_locations:
        page_url = poi_html.xpath(".//@data-href")[0]
        location_name = poi_html.xpath(".//h4/a/text()")[0]
        street_address = poi_html.xpath(".//li/text()")[0]
        phone = poi_html.xpath('.//a[@class="tel"]/text()')[0]
        geo = (
            poi_html.xpath('.//a[contains(@href, "position")]/@href')[0]
            .split("=")[1]
            .split("&")[0]
            .split(",")
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city="",
            state="",
            zip_postal="",
            country_code="CN",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[0],
            longitude=geo[1],
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
