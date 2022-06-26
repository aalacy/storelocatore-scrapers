import json
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re


DOMAIN = "citybankonline.com"
BASE_URL = "https://www.city.bank/locations/details"
LOCATION_URL = "https://www.city.bank/locations"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    req = session.get(url, headers=HEADERS)
    if req.status_code == 200:
        soup = bs(req.content, "lxml")
    else:
        return False
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    data = json.loads(soup.find("location-finder")[":locations"])
    for row in data:
        page_url = BASE_URL + row["Url"]
        location_name = row["Title"]
        street_address = row["Street"].strip()
        city = row["City"]
        state = row["State"]
        zip_postal = row["Zip"]
        country_code = "US"
        phone = row["Phone"]
        hours_of_operation = " ".join(
            re.sub(
                r"Lobby Hours|Hours|Drive Thru|ATM|This location.*",
                "",
                bs(row["Hours"], "lxml").get_text(strip=True, separator=" "),
            ).split()
        )
        location_type = ",".join(row["Types"])
        store_number = MISSING
        latitude = row["Latitude"]
        longitude = row["Longitude"]
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
