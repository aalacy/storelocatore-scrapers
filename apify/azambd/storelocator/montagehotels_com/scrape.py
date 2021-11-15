import time
import json
import re
from lxml import html

from sgrequests import SgRequests
from sgselenium.sgselenium import SgChrome
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

DOMAIN = "montagehotels.com"
website = "https://www.montagehotels.com"
MISSING = SgRecord.MISSING

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
}

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)
session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def request_with_retries(url):
    return session.get(url, headers=headers)


def get_driver(url):
    x = 0
    while True:
        x = x + 1
        try:
            driver = SgChrome(user_agent=user_agent, is_headless=True).driver()
            driver.get(url)
            return driver.page_source
        except Exception:
            driver.quit()
            if x == 10:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue


def getJSObject(response, varName, noVal=MISSING):
    JSObject = re.findall(f'{varName}: "(.+?)",', response)
    if JSObject is None or len(JSObject) == 0:
        return noVal
    return JSObject[0]


def fetch_stores():
    response = get_driver(f"{website}/deervalley/")

    body = html.fromstring(response, "lxml")
    storeUrls = body.xpath('//select[@id="destination-selector"]/option/@data-url')
    return storeUrls


def fetch_data():
    storeUrls = fetch_stores()
    log.info(f"Total stores = {len(storeUrls)}")
    for page_url in storeUrls:
        log.debug(f"Scrapping {page_url} ...")
        response = get_driver(page_url)
        store_number = getJSObject(response, "hotel")
        log.info(f"Store Number: {store_number}")
        response = request_with_retries(
            f"https://newbooking.azds.com/api/hotel/{store_number}/configuration?lang=en"
        )
        data = json.loads(response.text)
        location_name = data["name"]
        log.info(f"Location Name: {location_name}")
        latitude = data["latitude"]
        log.info(f"Latitude: {latitude}")
        longitude = data["longitude"]
        log.info(f"Longitude: {longitude}")
        try:
            phone = data["phone"]
            log.info(f"Phone: {phone}")
        except:
            phone = MISSING
            log.info(
                f"Phone Number is not available in the API Endpoint, Store Number: {store_number}"
            )

        city = data["city"]
        raw_address = data["address"]

        [street_address, part2] = raw_address.split(", ")
        [state, zip_postal] = part2.split(" ")
        yield SgRecord(
            locator_domain=DOMAIN,
            store_number=store_number,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=zip_postal,
            state=state,
            country_code="US",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            raw_address=raw_address,
        )


def scrape():
    log.info("Started")
    count = 0
    start = time.time()

    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        result = fetch_data()
        for rec in result:
            writer.write_row(rec)
            count = count + 1

    end = time.time()
    log.info(f"Total Rows Added= {count}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
