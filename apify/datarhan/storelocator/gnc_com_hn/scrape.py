from time import sleep
from lxml import etree

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    start_url = "https://www.gnc.com.hn/sucursales/"
    domain = "gnc.com.hn"

    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(15)
        driver.find_element_by_xpath('//span[@class="hustle-icon-close"]').click()
        sleep(3)
        dom = etree.HTML(driver.page_source)
        all_names = dom.xpath("//div/div/h6/text()")

        all_locations = driver.find_elements_by_xpath("//div[div[h6]]")
        for i, e in enumerate(all_locations):
            location_name = all_names[i]
            hoo = dom.xpath(
                f'.//h6[contains(text(), "{location_name}")]/following-sibling::p/text()'
            )
            hoo = " ".join([h.strip() for h in hoo])

            driver.switch_to.frame(e.find_element_by_xpath(f".//iframe"))
            loc_dom = etree.HTML(driver.page_source)
            raw_address = loc_dom.xpath('//div[@class="address"]/text()')[0]
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2
            geo = (
                loc_dom.xpath('//a[@class="navigate-link"]/@href')[0]
                .split("/@")[-1]
                .split(",")[:2]
            )
            driver.switch_to.default_content()

            item = SgRecord(
                locator_domain=domain,
                page_url=start_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=addr.country,
                store_number="",
                phone="",
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
