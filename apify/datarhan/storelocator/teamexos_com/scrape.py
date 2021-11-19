from lxml import etree
from time import sleep

from sgselenium.sgselenium import SgFirefox
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    start_url = "https://www.teamexos.com/"
    domain = "teamexos.com"

    with SgFirefox() as driver:
        driver.get(start_url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.find_element_by_xpath(
            '//li[@class="footer-links-component__item"]/a[contains(text(), "Contact us")]'
        ).click()
        sleep(10)
        dom = etree.HTML(driver.page_source)

        all_locations = dom.xpath('//div[@class="location-list__location-card"]')
        for poi_html in all_locations:
            location_name = poi_html.xpath(
                './/div[@class="location-list__location-card-title"]/text()'
            )[0]
            raw_address = poi_html.xpath(
                './/div[@class="location-list__location-card-address"]/text()'
            )
            phone = poi_html.xpath(
                './/div[@class="location-list__location-card-phone"]/text()'
            )
            phone = phone[0] if phone else ""
            location_type = poi_html.xpath(
                './/div[@class="location-list__filters-item-title"]/text()'
            )
            location_type = " ".join(location_type)

            item = SgRecord(
                locator_domain=domain,
                page_url=start_url,
                location_name=location_name,
                street_address=raw_address[0],
                city=raw_address[1].split(", ")[0],
                state=raw_address[1].split(", ")[-1].split()[0],
                zip_postal=raw_address[1].split(", ")[-1].split()[-1],
                country_code="",
                store_number="",
                phone=phone,
                location_type=location_type,
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
