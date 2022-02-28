from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_usa
import re
from sgselenium import SgSelenium
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

DOMAIN = "milios.com"
BASE_URL = "https://milios.com"
LOCATION_URL = "https://milios.com/stores/"
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
            data = parse_address_usa(raw_address)
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


def get_latlong(element):
    try:
        latitude = re.search(r"lat:\s(-?[\d]*\.[\d]*)", element.string)
        longitude = re.search(r"lng:\s(-[\d]*\.[\d]*)", element.string)
        return latitude.group(1), longitude.group(1)
    except:
        return MISSING, MISSING


def fetch_data():
    log.info("Fetching store_locator data")
    driver = SgSelenium().chrome()
    driver.get(LOCATION_URL)
    driver.implicitly_wait(10)
    soup = bs(driver.page_source, "lxml")
    driver.quit()
    contents = soup.find("div", {"class": "store-results"}).find_all(
        "a", {"class": "location-direction"}
    )
    for row in contents:
        page_url = row["href"]
        content = pull_content(page_url)
        info = (
            content.find("div", {"class": "address-locator"})
            .get_text(strip=True, separator="@")
            .split("@")
        )
        location_name = (
            content.find("div", {"class": "location-info-left"}).find("h1").text.strip()
        )
        raw_address = " ".join(info[:-1])
        street_address, city, state, zip_postal = getAddress(raw_address)
        if "Madison" in street_address and city == MISSING:
            city = "Madison"
            street_address = street_address.replace(city, "").strip()
        phone = info[-1]
        hours_of_operation = (
            content.find("div", {"class": "location-info-left"})
            .find("ul")
            .get_text(strip=True, separator=",")
            .replace("day,", "day: ")
        )
        country_code = "US"
        store_number = MISSING
        location_type = MISSING
        coord = content.find("script", string=re.compile(r".*lat:\s(-?[\d]*\.[\d]*)"))
        latitude, longitude = get_latlong(coord)
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
