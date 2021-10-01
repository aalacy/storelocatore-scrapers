import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

DOMAIN = "o2fitnessclubs.com"
BASE_URL = "https://www.o2fitnessclubs.com"
LOCATION_URL = "https://www.o2fitnessclubs.com/locations"
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


MISSING = "<MISSING>"


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
    HEADERS["Referer"] = url
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def parse_hours(element):
    if not element:
        return "<MISSING>"
    days = [val.text for val in element.find_all("p", text=re.compile(r"day.*"))]
    hours = [
        val.text for val in element.find_all("h5", text=re.compile(r"\d{1,2}\s+am|pm"))
    ]
    hoo = []
    for i in range(len(days)):
        hoo.append(
            "{}: {}".format(days[i].replace("–", "-"), hours[i].replace("–", "-"))
        )
    return ", ".join(hoo)


def fetch_store_urls():
    log.info("Fetching store URL")
    store_urls = []
    soup = pull_content(LOCATION_URL)
    content = soup.find_all("div", {"class": "hs-accordion__item-content"})
    for row in content:
        stores = row.find("ul").find_all("a")
        for link in stores:
            store_urls.append(BASE_URL + link["href"])
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def get_latlong(soup):
    content = soup.find("script", string=re.compile(r"center\:\s+\[(.*)\]"))
    if not content:
        return "<MISSING>", "<MISSING>"
    latlong = re.search(r"center\:\s+\[(.*)\]", content.string).group(1).split(",")
    return latlong[0].strip(), latlong[1].strip()


def wait_load(driver, number=0):
    number += 1
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "location-description"))
        )
    except:
        driver.refresh()
        if number < 3:
            log.info(f"Try to Refresh for ({number}) times")
            return wait_load(driver, number)


def fetch_data():
    log.info("Fetching store_locator data")
    store_urls = fetch_store_urls()
    driver = SgSelenium().chrome()
    for page_url in store_urls:
        page_url = page_url.replace("?hsLang=en", "")
        driver.get(page_url)
        wait_load(driver)
        soup = bs(driver.page_source, "lxml")
        comming_soon = soup.find("div", {"class": "location-description"}).find("h6")
        if comming_soon and "COMING SOON" in comming_soon:
            continue
        location_name = soup.find("title").text.strip()
        raw_address = (
            soup.find("div", {"class": "location-details"})
            .get_text(strip=True, separator=",")
            .split(",")
        )
        phone = raw_address[-1]
        del raw_address[-1]
        street_address, city, state, zip_postal = getAddress(", ".join(raw_address))
        country_code = "US"
        store_number = re.search(
            r"\?store_id=(\d+)",
            soup.find("a", {"href": re.compile(r"\?store_id=\d+")})["href"],
        ).group(1)
        hours_of_operation = parse_hours(soup.find("div", {"class": "location-hours"}))
        latitude, longitude = get_latlong(soup)
        location_type = "<MISSING>"
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
    with SgWriter(SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
