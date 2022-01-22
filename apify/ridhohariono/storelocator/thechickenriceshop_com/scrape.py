from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re

DOMAIN = "thechickenriceshop.com"
LOCATION_URL = "https://www.thechickenriceshop.com/find-us"
API_URL = "https://www.thechickenriceshop.com/wp-content/themes/hello-elementor-child/outlets.json"
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
    days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    for row in data:
        location_name = re.sub(r"\d+\.", "", row["name"])
        city = row["city"]
        state = row["state"]
        zip_postal = row["postcode"]
        street_address = (
            re.sub(
                city + r".*|" + state + r".*|" + str(zip_postal) + r".*",
                "",
                row["address"],
            )
            .strip()
            .rstrip(",")
        )
        phone = row["contact"]
        country_code = "MY"
        hoo = ""
        for day in days:
            hoo += day.title() + ": " + row[day] + ","
        hours_of_operation = hoo.strip().rstrip(",")
        location_type = MISSING
        store_number = row["name"].split(".")[0]
        latitude = row["latitude"]
        longitude = row["logitude"]
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
