from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "radley.co.uk"
BASE_URL = "https://radley.co.uk"
LOCATION_URL = "https://www.radley.co.uk/stores/"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
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


def get_latlong(url):
    latlong = re.search(r"coord=(-?[\d]*\.[\d]*),\s+(-?[\d]*\.[\d]*)", url)
    if not latlong:
        latlong = re.search(r"coord=(-?[\d]*\.[\d]*),(-?[\d]*\.[\d]*)", url)
        if not latlong:
            return "<MISSING>", "<MISSING>"
    return latlong.group(1), latlong.group(2)


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    page_urls = soup.find_all("div", {"align": "center"})[1].find_all("a")
    for row in page_urls:
        page_url = row["href"]
        content = pull_content(page_url)
        info = content.find("div", {"class": "inner"})
        location_name = (
            content.find("h4", {"class": "homepage-heading"}).text.split(":")[0].strip()
        )
        addr_phone = (
            info.find("h4", text=re.compile(r"ADDRESS.*PHONE", re.IGNORECASE))
            .find_next("p", {"class": "homepage-text"})
            .get_text(strip=True, separator="@@")
            .replace("Address: ", "")
            .replace("Phone: ", "")
            .split("@@")
        )
        raw_address = addr_phone[0]
        street_address, city, state, zip_postal = getAddress(raw_address)
        phone = addr_phone[1]
        hours_of_operation = (
            info.find("table", {"class": "delivery-table"})
            .get_text(strip=True, separator=",")
            .replace("day,", "day: ")
        )
        country_code = "UK"
        store_number = MISSING
        location_type = "radley_uk"
        try:
            map_link = info.find("iframe")["src"]
            latitude, longitude = get_latlong(map_link)
        except:
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
