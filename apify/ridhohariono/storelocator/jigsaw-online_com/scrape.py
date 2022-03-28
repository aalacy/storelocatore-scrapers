import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "jigsaw-online.com"
BASE_URL = "https://jigsaw-online.com"
LOCATION_URL = "https://www.jigsaw-online.com/pages/store-locator"
API_URL = "https://jigsawimagestorage.blob.core.windows.net/jigsaw-logos/google-map-data-V3.json"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    stores = session.get(API_URL, headers=HEADERS).json()
    for row in stores["features"]:
        info = row["properties"]
        location_name = info["branch_name"]
        street_address = info["branch_address_2"]
        state = MISSING
        city = info["branch_city"]
        zip_postal = info["branch_postcode"]
        phone = info["branch_phone"]
        hours_of_operation = (
            info["branch_opening_hours"]
            .replace("</li><li>", ",")
            .replace("<li>", "")
            .replace("</li>", "")
        )
        store_number = re.sub(r"\D+", "", info["branch_info"])
        country_code = info["branch_country"]
        location_type = row["type"]
        latitude = row["geometry"]["coordinates"][1]
        longitude = row["geometry"]["coordinates"][0]
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=LOCATION_URL,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address}, {city}, {zip_postal}",
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
