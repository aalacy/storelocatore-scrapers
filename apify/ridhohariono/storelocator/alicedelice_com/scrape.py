from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json
from datetime import datetime
from datetime import timezone

DOMAIN = "alicedelice.com"
BASE_URL = "https://www.alicedelice.com"
LOCATION_URL = "https://www.alicedelice.com/trouver-ma-boutique"
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
    soup = pull_content(LOCATION_URL)
    contents = json.loads(soup.find("stores")["stores"])
    for row in contents:
        page_url = BASE_URL + row["URL"]
        location_name = row["FullName"].strip()
        street_address = row["Address"]
        city = row["City"]
        state = MISSING
        zip_postal = row["PostCode"]
        country_code = "FR"
        phone = row["Phone"]
        store_number = row["IDCard"]
        location_type = MISSING
        hoo = ""
        for date in row["OpeningHours"]:
            day = (
                datetime.fromisoformat(date["Date"])
                .astimezone(timezone.utc)
                .strftime("%A: ")
            )
            if date["IsOpen"]:
                start = ":".join(date["Date1Start"].split("T")[1].split(":")[:-1])
                end = ":".join(date["Date1End"].split("T")[1].split(":")[:-1])
                hoo += day + start + "-" + end + ", "
            else:
                hoo += day + "Closed, "
        hours_of_operation = hoo.strip().rstrip(",")
        latitude = row["Coordinate"]["Latitude"]
        longitude = row["Coordinate"]["Longitude"]
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
