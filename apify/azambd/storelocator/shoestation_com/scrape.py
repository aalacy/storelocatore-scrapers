from lxml import html
import ssl
import time
import json

from sgselenium.sgselenium import SgChrome
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


ssl._create_default_https_context = ssl._create_unverified_context

website = "https://www.shoestation.com"
page_url = f"{website}/storelocator/"
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)


def jsonjson(response):
    return response.split('"items":')[1].split("]")[0]


def stringify_children(nodes):
    values = []
    for node in nodes:
        for text in node.itertext():
            if text:
                values.append(text.strip())
    if len(values) == 0:
        return MISSING
    return " ".join(" ".join(values).split())


def fetch_stores():
    with SgChrome(user_agent=user_agent) as driver:
        driver.get(page_url)

        time.sleep(30)
        body = html.fromstring(driver.page_source, "lxml")
        locations = jsonjson(driver.page_source)
        storePages = body.xpath('//div[contains(@class, "amlocator-store-desc")]')

        stores = []
        for storePage in storePages:
            text = stringify_children([storePage])
            stores.append(text)
        return stores, json.loads(locations + "]")


def fetch_data():
    stores, locations = fetch_stores()
    log.info(f"Total stores = {len(stores)}")

    location_type = MISSING
    phone = MISSING
    country_code = "US"
    count = 0

    for store in stores:
        count = count + 1
        location = locations[count - 1]
        store_number = str(location["id"])
        latitude = str(location["lat"])
        longitude = str(location["lng"])

        store = store.split("City:")

        location_name = store[0].strip()
        store = store[1].split("Zip:")
        city = store[0].strip()
        store = store[1].split("State:")
        zip_postal = store[0].strip()
        store = store[1].split("Address:")
        state = store[0].strip()
        store = store[1].split("Distance:")
        street_address = store[0].strip()
        store = store[1].split("Monday")
        hours_of_operation = ("Monday" + store[1]).strip()
        raw_address = f"{street_address} {city}, {state} {zip_postal}"

        yield SgRecord(
            locator_domain="shoestation.com",
            store_number=store_number,
            page_url=page_url,
            location_name=location_name,
            location_type=location_type,
            street_address=street_address,
            city=city,
            zip_postal=zip_postal,
            state=state,
            country_code=country_code,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )
    return []


def scrape():
    log.info(f"Start Crawling {website} ...")
    start = time.time()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
