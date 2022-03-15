import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "nicoletbank.com"
BASE_URL = "https://nicoletbank.com"
LOCATION_URL = "https://www.nicoletbank.com/branch-atm-locations"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()
MISSING = "<MISSING>"


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def is_multiple(location_name, locations):
    for row in locations:
        if location_name in row:
            return False
    return True


def get_hoo(link):
    soup = pull_content(link)
    hoo = soup.find("div", {"class": "branch-hours"}).find_all("p")
    hours_of_operations = (
        hoo[1]
        .get_text(strip=True, separator=",")
        .replace("Lobby Hours,", "")
        .replace("day,", "day: ")
    )
    return hours_of_operations


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    content = (
        soup.find("div", {"class": "locator-branches"})
        .find("div", {"class": "branches"})
        .find("div", {"class": "branch-scroll"})
        .find_all("div", {"class": "branch"})
    )
    for row in content:
        page_url = BASE_URL + row.find("a", {"class": "branch-ico"})["href"]
        location_name = row["data-asodata1"].strip()
        street_address = row["data-asodata2"].strip()
        city_state = row["data-asodata3"].split(",")
        city = city_state[0]
        state = re.sub(r"\d+", "", city_state[1]).replace("-", "").strip()
        zip_postal = re.sub(r"\D+", "", city_state[1].split("-")[0]).strip()
        country_code = "US"
        store_number = MISSING
        phone = row["data-info-address"].split("<br />")[1].strip()
        hours_of_operation = get_hoo(page_url)
        location_type = "BRANCH_ATM"
        latitude = row["data-latitude"]
        longitude = row["data-longitude"]
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code=country_code,
            store_number=store_number,
            phone=phone.strip(),
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
