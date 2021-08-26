import re
from lxml import html
import time
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID

from sgselenium.sgselenium import SgChrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

DOMAIN = "lmcu.org"

MISSING = SgRecord.MISSING

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def initiate_driver(url, class_name, driver=None):
    if driver is not None:
        driver.quit()

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    x = 0
    while True:
        x = x + 1
        try:
            driver = SgChrome(
                user_agent=user_agent,
            ).driver()
            driver.get(url)

            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            break
        except Exception:
            driver.quit()
            if x == 10:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver


def fetch_data():
    url = "https://www.lmcu.org/locations/branch-listing"
    driver = initiate_driver(url, "entry-content")
    htmlpage = driver.page_source
    tree = html.fromstring(htmlpage, "lxml")
    tr = tree.xpath("//table//tr[./td[@data-title]]")
    for t in tr:
        page_url = url
        location_name = (
            "".join(t.xpath('.//div[@class="contact-name"]//text()'))
            .replace("\n", "")
            .strip()
        )
        log.info(f"Grabbing Location: {location_name}")
        location_type = "Branch"
        street_address = (
            "".join(t.xpath('.//div[@class="branch-address"]/a/text()[1]'))
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(t.xpath('.//div[@class="branch-address"]/a/text()[2]'))
            .replace("\n", "")
            .strip()
        )
        phone = (
            "".join(t.xpath('.//div[@class="branch-phone"]/text()'))
            .replace("\n", "")
            .strip()
            or MISSING
        )
        map_link = "".join(
            t.xpath('.//div[@class="branch-address"]/a/@href[1]')
        ).strip()
        try:
            geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{1,3}\.[0-9]+", map_link)[
                0
            ].split(",")
            latitude = geo[0]
            longitude = geo[1]
        except:
            latitude = MISSING
            longitude = MISSING

        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = MISSING
        hours_of_operation = (
            " ".join(t.xpath('.//div[@class="branch-hour"]/div//text()'))
            .replace("\n", "")
            .strip()
        )

        raw_address = f"{street_address}, {city}, {state} {postal}"

        yield SgRecord(
            locator_domain=DOMAIN,
            store_number=store_number,
            page_url=page_url,
            location_name=location_name,
            location_type=location_type,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            state=state,
            country_code=country_code,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )
    driver.quit()


def scrape():
    log.info("Crawling Started")
    count = 0
    start = time.time()
    result = fetch_data()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for rec in result:
            writer.write_row(rec)
            count = count + 1

    end = time.time()
    log.info(f"Total Rows Added= {count}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
