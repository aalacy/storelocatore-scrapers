from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re

DOMAIN = "awg-mode.de"
BASE_URL = "https://www.awg-mode.de"
API_URL = "https://www.awg-mode.de/store-locator?lat=52.52000659999999&lon=13.404954&distance=50000km"
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


def get_hoo(url):
    soup = pull_content(url)
    hours_of_operation = (
        soup.find("strong", text=re.compile("Öffnungszeiten"))
        .find_next("ul")
        .get_text(strip=True, separator=",")
        .replace(":,", ": ")
        .strip()
    )
    return hours_of_operation


def fetch_data():
    log.info("Fetching store_locator data")
    data = session.get(API_URL, headers=HEADERS).json()["storeLocations"]
    for row in data:
        page_url = BASE_URL + row["url"]
        location_name = row["name"]
        if not row["address2"]:
            street_address = row["address1"].strip()
        else:
            street_address = (row["address1"] + ", " + row["address2"]).strip()
        city = row["city"]
        state = MISSING
        zip_postal = row["zip"]
        phone = row["phone"]
        country_code = "DE"
        hours_of_operation = get_hoo(page_url)
        location_type = MISSING
        store_number = row["id_store_location"]
        latitude = row["location"]["latitude"]
        longitude = row["location"]["longitude"]
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
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
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
