from lxml import etree
from time import sleep

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    start_url = "https://www.burrachos.com/locations/"
    domain = "burrachos.com"

    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(10)
        dom = etree.HTML(driver.page_source)

        all_locations = dom.xpath(
            '//div[div[div[div[div[h2[span[contains(text(), "LOCATION")]]]]]]]'
        )[1:]
        for poi_html in all_locations:
            raw_address = poi_html.xpath('.//a[contains(@href, "maps")]/text()')
            phone = (
                poi_html.xpath('.//a[contains(@href, "tel")]/text()')[0]
                .split(":")[-1]
                .strip()
            )
            zip_code = raw_address[1].split(", ")[-1].split()[-1].strip()
            hoo = poi_html.xpath(
                './/div[h2[span[contains(text(), "HOURS")]]]/following-sibling::div//text()'
            )
            hoo = " ".join([e.strip() for e in hoo if e.strip()])
            driver.switch_to.frame(
                driver.find_element_by_xpath(
                    "//iframe[contains(@src, '{}')]".format(zip_code)
                )
            )
            poi_dom = etree.HTML(driver.page_source)
            geo = (
                poi_dom.xpath('//a[contains(@href, "@")]/@href')[0]
                .split("@")[-1]
                .split(",")[:2]
            )
            driver.switch_to.default_content()

            item = SgRecord(
                locator_domain=domain,
                page_url=start_url,
                location_name="",
                street_address=raw_address[0],
                city=raw_address[1].split(", ")[0],
                state=raw_address[1].split(", ")[-1].split()[0],
                zip_postal=zip_code,
                country_code="",
                store_number="",
                phone=phone,
                location_type="",
                latitude=geo[0],
                longitude=geo[1],
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
