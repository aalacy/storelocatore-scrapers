from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "ramsdensforcash.co.uk"
BASE_URL = "https://www.ramsdensforcash.co.uk"
SITE_MAP = "https://www.ramsdensforcash.co.uk/footer-links/about-this-site/site-map/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def getAddress(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_intl(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode
            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            return street_address, city, state, zip_postal
    except Exception as e:
        log.info(f"No valid address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(SITE_MAP)
    contents = soup.find("a", text="Branches").find_next("ul").find_all("a")
    for row in contents:
        try:
            page_url = BASE_URL + row["href"]
        except:
            continue
        store = pull_content(page_url)
        is_coming_soon = store.find("table", {"bordercolor": "#ff0000"})
        if is_coming_soon and "TEMPORARILY CLOSED" in is_coming_soon.text.strip():
            continue
        location_name = store.find("h1", id="branchName").text.strip()
        raw_address = (
            store.find("div", id="branchAddress")
            .get_text(strip=True, separator=",")
            .replace("Address:,", "")
            .replace(" ", "")
            .strip()
        )
        street_address, city, state, zip_postal = getAddress(raw_address)
        phone = (
            store.find("div", id="branchTelephone")
            .text.replace("Telephone:", "")
            .strip()
        )
        hoo_content = store.find("div", id="standardOpeningTimes")
        hoo_content.find("span", {"class": "branch-opening-hours-heading"}).decompose()
        hours_of_operation = re.sub(
            r"Please note opening times are subject to flight schedule changes.,",
            "",
            hoo_content.get_text(strip=True, separator=",")
            .replace("day,", "day: ")
            .replace(" ", "")
            .replace(",-,", " - ")
            .strip(),
        )
        location_type = MISSING
        country_code = "GB"
        store_number = MISSING
        latitude = MISSING
        longitude = MISSING
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
            raw_address=raw_address,
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
