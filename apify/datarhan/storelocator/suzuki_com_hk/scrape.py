from lxml import etree
from time import sleep

from sgselenium.sgselenium import SgFirefox
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    start_url = "http://suzuki.com.hk/ContactUS#Showroom"
    domain = "suzuki.com.hk"

    with SgFirefox() as driver:
        driver.get(start_url)
        driver.find_element_by_xpath('//div[@id="language"]//button').click()
        driver.find_element_by_xpath(
            '//div[@id="language"]//a[contains(text(), "EN")]'
        ).click()
        sleep(5)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//div[p[strong[contains(text(), "Address")]]]')
    for poi_html in all_locations:
        location_name = (
            poi_html.xpath(".//p/strong/text()")[0].replace("Address", "").strip()
        )
        raw_data = [e.strip() for e in poi_html.xpath(".//p/text()") if e.strip()]
        street_address = " ".join(raw_data[:2]).split("(")[0]
        phone = [e.replace("Tel: ", "") for e in raw_data if "Tel:" in e][0]
        hoo = [e for e in raw_data if "Mon -" in e][0]
        city = location_name.split("Showroom")[0].strip()
        geo = (
            dom.xpath('.//iframe[contains(@src, "Hong")]/@src')[0]
            .split("!2d")[-1]
            .split("!3m")[0]
            .split("!3d")
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal="",
            country_code="HK",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[1],
            longitude=geo[0],
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
