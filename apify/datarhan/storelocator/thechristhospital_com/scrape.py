import ssl
from lxml import etree
from time import sleep

from sgselenium import SgChrome
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def fetch_data():
    domain = "thechristhospital.com"
    start_url = "https://www.thechristhospital.com/locations"
    all_locations = []
    with SgChrome() as driver:
        driver.get(start_url)
        sleep(3)
        driver.find_element_by_id("btnSearchAdvanced").click()
        sleep(5)
        dom = etree.HTML(driver.page_source)
        all_locations += dom.xpath('//div[@class="location"]')
        next_page = driver.find_element_by_xpath('//a[contains(@id, "PageFwd")]')
        while next_page:
            next_page.click()
            sleep(20)
            dom = etree.HTML(driver.page_source)
            all_locations += dom.xpath('//div[@class="location"]')
            try:
                next_page = driver.find_element_by_xpath(
                    '//a[contains(@id, "PageFwd")]'
                )
            except Exception:
                next_page = ""

    for poi_html in all_locations:
        page_url = "https://www.thechristhospital.com/locations"
        own_url = poi_html.xpath('.//a[@class="location-header"]/@href')
        if own_url:
            page_url = own_url[0]
        location_name = poi_html.xpath(
            './/span[@class="location-header no-details-link"]/text()'
        )
        if not location_name:
            location_name = poi_html.xpath('.//a[@class="location-header"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi_html.xpath('.//span[@class="addressline"]/text()')[
            0
        ].strip()
        address_2 = poi_html.xpath('.//span[@class="addressline addressline2"]/text()')
        if address_2:
            street_address += ", " + address_2[0].strip()
        address_raw = poi_html.xpath('.//span[@class="addressline"]/text()')
        address_raw = [elem.strip() for elem in address_raw if elem.strip()]
        city = address_raw
        city = city[-1].strip().split(",")[0] if city else "<MISSING>"
        state = address_raw
        state = state[-1].strip().split(",")[-1].split()[0] if state else "<MISSING>"
        zip_code = address_raw
        zip_code = (
            zip_code[-1].strip().split(",")[-1].split()[-1] if zip_code else "<MISSING>"
        )
        phone = poi_html.xpath('.//span[@class="phonenumber"]/b/text()')
        phone = [e.strip() for e in phone if e.strip()]
        phone = phone[0].strip() if phone else "<MISSING>"
        hours_of_operation = poi_html.xpath(
            './/h2[contains(text(), "Hours")]/following-sibling::dl//text()'
        )
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=SgRecord.MISSING,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
