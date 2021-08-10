import re
import ssl
from lxml import etree
from time import sleep

from sgselenium.sgselenium import SgChrome
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgscrape.sgpostal import parse_address_intl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def fetch_data():
    # Your scraper here
    start_url = "https://myxperiencefitness.com/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    with SgChrome() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

        all_locations = dom.xpath("//h4/a[contains(@href, '/gyms/')]/@href")
        for store_url in list(set(all_locations)):
            driver.get(store_url)
            sleep(10)
            loc_dom = etree.HTML(driver.page_source)

            location_name = loc_dom.xpath('//h1[@class="entry-title"]/text()')
            location_name = location_name[0] if location_name else "<MISSING>"
            raw_address = loc_dom.xpath('//a[@class="foot-address-link"]/text()')[0]
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            if street_address.endswith("Blaine"):
                street_address = street_address.replace(" Blaine", "")
            city = " ".join(store_url.split("/")[-2].split("-")[:-2])
            state = store_url.split("/")[-2].split("-")[-2]
            zip_code = store_url.split("/")[-2].split("-")[-1]
            if "blaine-south-mn" in store_url:
                city = "blaine south"
                state = "mn"
                zip_code = "<MISSING>"
            country_code = "US"
            phone = loc_dom.xpath('//a[@class="details-phone-link"]/text()')[0]
            hoo = loc_dom.xpath(
                '//th[i[@class="fas fa-clock"]]/following-sibling::td/text()'
            )
            if not hoo:
                hoo = loc_dom.xpath('//h6[contains(text(), "Mon –")]/text()')
            hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = (
                " ".join(hoo).split("Dec 19 ")[-1].split(" XF")[0]
                if hoo
                else "<MISSING>"
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
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
