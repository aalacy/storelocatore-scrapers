from lxml import etree
from urllib.parse import urljoin
from time import sleep

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    start_url = "https://www.lexus.ae/en/our-locations/"
    domain = "lexus.ae"
    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

        all_locations = dom.xpath('//a[contains(text(), "Discover location")]/@href')
        for page_url in list(set(all_locations)):
            page_url = urljoin(start_url, page_url)
            if "service-center" in page_url:
                continue
            driver.get(page_url)
            sleep(5)
            driver.switch_to.frame(
                driver.find_element_by_xpath('//iframe[contains(@src, "maps")]')
            )
            loc_dom = etree.HTML(driver.page_source)
            location_name = loc_dom.xpath('//div[@class="place-name"]/text()')[0]
            raw_address = loc_dom.xpath('//div[@class="address"]/text()')[0].replace(
                " - ", ", "
            )
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2
            geo = (
                loc_dom.xpath('//a[@class="navigate-link"]/@href')[0]
                .split("/@")[-1]
                .split(",")[:2]
            )
            driver.switch_to.default_content
            loc_dom = etree.HTML(driver.page_source)
            phone = loc_dom.xpath('//p[contains(text(), "Call")]/text()')
            phone = phone[-1] if phone else ""

            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)
            hoo = loc_dom.xpath(
                '//p[contains(text(), "SALES")]/following-sibling::table//text()'
            )
            if not hoo:
                hoo = loc_dom.xpath(
                    '//p[contains(text(), "PRE-OWNED")]/following-sibling::table//text()'
                )
            if not hoo:
                hoo = loc_dom.xpath(
                    '//p[strong[contains(text(), "SALES")]]/following-sibling::table//text()'
                )
            hoo = [e.replace("\xa0", "").strip() for e in hoo if e.strip()]
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state="",
                zip_postal=addr.postcode,
                country_code="AE",
                store_number="",
                phone=phone,
                location_type="",
                latitude=geo[0],
                longitude=geo[1],
                hours_of_operation=hoo,
                raw_address=raw_address,
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
