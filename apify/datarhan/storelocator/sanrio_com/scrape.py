from time import sleep
from lxml import etree

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    domain = "sanrio.com"
    start_url = "https://www.sanrio.com/pages/store-locator"

    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(10)
        dom = etree.HTML(driver.page_source)
    all_locations = dom.xpath('//li[@id="scasl-list-container"]')

    for poi_html in all_locations:
        location_name = poi_html.xpath('.//div[@id="scasl-title"]/text()')[0]
        street_address = poi_html.xpath('.//div[@id="scasl-address"]/text()')[0]
        city = poi_html.xpath('.//span[@id="scasl-city"]/text()')[0]
        state = poi_html.xpath('.//span[@id="scasl-state"]/text()')
        state = state[0] if state else ""
        zip_code = poi_html.xpath('.//span[@id="scasl-zipcode"]/text()')[0]
        phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')[0]
        country_code = poi_html.xpath('.//span[@id="scasl-country"]/text()')
        country_code = country_code[0] if country_code else ""
        hoo = poi_html.xpath('.//div[@id="scasl-schedule"]/text()')
        hoo = " ".join(" ".join(hoo).split()) if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
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
