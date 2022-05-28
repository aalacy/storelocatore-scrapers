# -*- coding: utf-8 -*-
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import time
from sgselenium.sgselenium import SgChrome  # noqa
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumwire import webdriver  # noqa
import ssl
from undetected_chromedriver import ChromeOptions
from sgpostal import sgpostal as parser

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

website = "rentokil.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.rentokil.co.uk",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def get_driver():
    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
    )
    options = ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--no-sandbox")  #
    options.add_argument("--disable-dev-shm-usage")  #
    options.add_argument("--ignore-certificate-errors")  #
    options.add_argument(f"user-agent={user_agent}")
    return webdriver.Chrome(
        options=options, executable_path=ChromeDriverManager().install()
    )


def check(url, class_name, driver):
    try:
        driver.get(url)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, class_name))
        )
        return True
    except Exception:
        driver.quit()
        return False


def Se(url, class_name):
    for c in range(10):
        time.sleep(5)
        driver = get_driver()
        if check(url, class_name, driver):
            return driver


def fetch_data():
    # Your scraper here
    search_url = "https://www.rentokil.co.uk/property-care/branches/"
    class_name = "menu"
    driver = Se(search_url, class_name)
    stores_sel = lxml.html.fromstring(driver.page_source)
    stores = stores_sel.xpath('//select[@id="menu"]/option[position()>1]/@value')
    for store_url in stores:
        page_url = "https://www.rentokil.co.uk" + store_url

        is_timeout = True
        while is_timeout is True:
            try:
                log.info(page_url)
                driver.get(page_url)
                is_timeout = False
            except:
                pass
        store_sel = lxml.html.fromstring(driver.page_source)

        locator_domain = website
        location_name = "".join(
            store_sel.xpath('//p[@class="section-title_header alpha"]/text()')
        ).strip()
        raw_address = ", ".join(
            list(filter(str, [x.strip() for x in store_sel.xpath("//address//text()")]))
        ).strip()

        city = location_name
        state = "<MISSING>"
        zip = "".join(store_sel.xpath('//span[@itemprop="postalCode"]/text()')).strip()

        formatted_addr = parser.parse_address_intl(raw_address)
        street_address = formatted_addr.street_address_1
        if street_address:
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2
        else:
            if formatted_addr.street_address_2:
                street_address = formatted_addr.street_address_2

        state = "<MISSING>"
        if not zip:
            zip = formatted_addr.postcode

        country_code = "GB"

        phone = "".join(
            store_sel.xpath('//span[@class="call-cta_number"]//text()')
        ).strip()
        location_type = "<MISSING>"
        store_number = "<MISSING>"

        latitude = "<MISSING>"
        longitude = "<MISSING>"

        hours_of_operation = "<MISSING>"

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
