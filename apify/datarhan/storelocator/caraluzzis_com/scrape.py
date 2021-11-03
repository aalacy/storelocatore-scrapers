import re
import ssl
from lxml import etree
from time import sleep
from urllib.parse import urljoin

from sgselenium import SgChrome
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sglogging import SgLogSetup

ssl._create_default_https_context = ssl._create_unverified_context

logger = SgLogSetup().get_logger("caraluzzis.com")


def fetch_data():
    start_url = "https://caraluzzis.com/locations/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")

    with SgChrome() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

        all_locations = dom.xpath('//div[@class="fl-rich-text"]/p/a[strong]')
        for poi_html in all_locations:
            store_url = urljoin(start_url, poi_html.xpath("@href")[0])
            if "https://store.caraluzzis.com/" in store_url:
                continue
            location_name = poi_html.xpath(".//strong/text()")
            location_name = " ".join(location_name) if location_name else "<MISSING>"

            driver.get(store_url)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            iframe = driver.find_element_by_xpath('//div[@class="fl-map"]/iframe')
            driver.switch_to.frame(iframe)
            sleep(15)
            loc_dom = etree.HTML(driver.page_source)
            geo = (
                loc_dom.xpath('//a[@class="navigate-link"]/@href')[0]
                .split("/@")[-1]
                .split(",")[:2]
            )
            driver.switch_to.default_content()
            loc_dom = etree.HTML(driver.page_source)

            raw_address = (
                loc_dom.xpath("//iframe/@src")[0]
                .split("q=")[-1]
                .split("&")[0]
                .replace("+", " ")
                .replace("%2C", "")
            )
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            city = city if city else "<MISSING>"
            state = addr.state
            state = state if state else "<MISSING>"
            zip_code = addr.postcode
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = addr.country
            country_code = country_code if country_code else "<MISSING>"
            store_number = "<MISSING>"
            phone = (
                loc_dom.xpath('//h5[@class="fl-heading"]/span/text()')[0]
                .split("•")[1]
                .strip()
            )
            location_type = "<MISSING>"
            latitude = geo[0]
            longitude = geo[1]
            hours_of_operation = (
                loc_dom.xpath('//h5[@class="fl-heading"]/span/text()')[0]
                .split("•")[2]
                .split("- Temp Hours")[0]
                .strip()
            )

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )

            yield item

        wine_locations = dom.xpath(
            '//div[@class="fl-rich-text" and p[strong[contains(text(), "Wine & Spirits")]]]'
        )
        for poi_html in wine_locations:
            store_url = poi_html.xpath(".//p/a/@href")[-1]
            location_name = " ".join(poi_html.xpath(".//strong/text()"))
            raw_data = poi_html.xpath(".//p/text()")
            raw_data = [e.strip() for e in raw_data if e.strip()]
            raw_address = raw_data[:2]
            if not raw_address:
                continue
            street_address = raw_address[0]
            city = raw_address[1].split(", ")[0]
            state = raw_address[1].split(", ")[-1].split()[0]
            zip_code = raw_address[1].split(", ")[-1].split()[-1]
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')
            phone = phone[0] if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hoo = raw_data[2:]
            hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
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
