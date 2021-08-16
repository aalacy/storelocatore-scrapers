import time
import json
from lxml import etree

from sgselenium import SgChrome
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from sglogging import sglog
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

MISSING = SgRecord.MISSING
DOMAIN = "theunionkitchen.com"

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
start_url = "https://www.theunionkitchen.com/locations"
user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)


def fetch_data():

    with SgChrome(user_agent=user_agent) as driver:
        driver.get(start_url)
        time.sleep(8)
        htmlSource = driver.page_source
        dom = etree.HTML(htmlSource)

    data = dom.xpath('//script[@class="js-react-on-rails-component"]/text()')[0]
    jdata = json.loads(data)
    locs = jdata["preloadQueries"][4]["data"]["restaurant"]["pageContent"]["sections"][
        0
    ]["locations"]
    for loc in locs:
        store_url = start_url
        street_address = loc["streetAddress"].replace("\n", "")
        if street_address.endswith(","):
            street_address = street_address[:-1]
        location_name = loc["name"]
        log.info(f"Location Name: {location_name}")
        city = loc["city"]
        state = loc["state"]
        zip_code = loc["postalCode"]
        raw_address = f"{street_address}, {city}, {state}, {zip_code}"
        country_code = loc["country"]
        store_number = loc["id"]
        phone = loc["phone"]
        location_type = MISSING
        latitude = loc["lat"]
        longitude = loc["lng"]
        hoo = loc["schemaHours"]
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo)

        log.info(f"Raw Address: {raw_address}")

        yield SgRecord(
            locator_domain=DOMAIN,
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
            raw_address=raw_address,
        )


def scrape():
    log.info("Started")
    count = 0
    start = time.time()
    result = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in result:
            writer.write_row(rec)
            count = count + 1

    end = time.time()
    log.info(f"Total Rows Added= {count}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
