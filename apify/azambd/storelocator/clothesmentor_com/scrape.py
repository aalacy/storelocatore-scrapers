import time
import json

from sgscrape.sgpostal import parse_address_intl
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sglogging import sglog

import ssl

ssl._create_default_https_context = ssl._create_unverified_context


DOMAIN = "clothesmentor.com"
MISSING = "<MISSING>"

website = "https://clothesmentor.com"

log = sglog.SgLogSetup().get_logger(logger_name=website)
api_url = "https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/8219/stores.js?callback=SMcallback2"


def get_driver(url, driver=None):
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
                executable_path=ChromeDriverManager().install(),
                user_agent=user_agent,
                is_headless=True,
            ).driver()
            driver.get(url)
            break
        except Exception:
            driver.quit()
            if x == 10:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver


# As selenium so cleaning HTML tags to get solid JSON
def getJsonObj(html_string):
    html_string = (
        html_string.replace("\n", "")
        .replace("\r", "")
        .replace("\t", "")
        .replace(")</pre></body></html>", "")
    )
    return html_string


def fetch_data():
    driver = get_driver(api_url)
    response = driver.page_source

    jsonobj = getJsonObj(response.split("SMcallback2(")[1])

    jsonData = json.loads(jsonobj)
    for d in jsonData["stores"]:
        store_number = d["id"]
        log.info(f"Fetching data from API and now at Store# {store_number}")
        phone = d["phone"]
        page_url = d["url"]
        latitude = d["latitude"]
        longitude = d["longitude"]
        street_address = d["address"]
        hours = d["custom_field_1"]
        hours_of_operation = hours.replace("&amp;", ",")
        location_name = d["name"]
        addrs = parse_address_intl(
            location_name.split("#")[0].replace("Store", "").strip()
        )
        if "," in location_name:
            city = location_name.split(", ")[0]
            state = location_name.split(", ")[-1].split()[0]
        else:
            city = addrs.city
            state = addrs.state

        location_type = "Store"
        country_code = "US"
        zip_postal = MISSING
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            phone=phone,
            location_type=location_type,
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

    driver.quit()


def scrape():
    log.info(f"Start Crawl {website} ...")
    count = 0
    start = time.time()
    result = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in result:
            writer.write_row(rec)
    end = time.time()
    log.info(f"Total Locations added = {count}")
    log.info(f"It took {end-start} seconds to complete the crawl.")


if __name__ == "__main__":
    scrape()
