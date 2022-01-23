from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re

DOMAIN = "fnbgriffin.com"
LOCATION_URL = "https://www.fnbgriffin.com/locations-and-hours"
API_URL = "https://www.fnbgriffin.com/_/api/branches/33.2453036/-84.2634769/50"
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
    data = session.get(API_URL, headers=HEADERS).json()
    for row in data["branches"]:
        location_name = row["name"]
        street_address = row["address"].strip()
        city = row["city"]
        state = row["state"]
        zip_postal = row["zip"]
        phone = row["phone"]
        country_code = "US"
        hours_of_operation = re.sub(
            r"\(Drive-ins only\),?|Drive-ins.*",
            "",
            bs(row["description"], "lxml")
            .get_text(strip=True, separator=",")
            .replace("day,", "day:")
            .strip(),
        ).rstrip(",")
        location_type = "BRANCH"
        if not row["active"]:
            location_type = "TEMP_CLOSED"
        store_number = MISSING
        latitude = row["lat"]
        longitude = row["long"]
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
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
