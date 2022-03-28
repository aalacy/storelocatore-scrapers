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
        dom = etree.HTML(driver.page_source)

        all_locations = dom.xpath('//div[@class="tab-panels"]/div')
        for poi_html in all_locations:
            poi_id = poi_html.xpath("@id")[0]
            driver.switch_to.frame(
                driver.find_element_by_xpath(f'//div[@id="{poi_id}"]/p/iframe')
            )
            loc_dom = etree.HTML(driver.page_source)
            location_name = loc_dom.xpath('//div[@class="place-name"]/text()')[0]
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
