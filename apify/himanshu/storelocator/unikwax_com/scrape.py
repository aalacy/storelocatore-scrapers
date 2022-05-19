import json
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import re
from selenium.webdriver.support.ui import WebDriverWait
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

DOMAIN = "unikwax.com"
BASE_URL = "https://unikwax.com"
LOCATION_URL = "https://unikwax.com/studio-locations/"
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


def wait_load(driver):
    try:
        WebDriverWait(driver, 5).until(
            lambda driver: driver.execute_script("return jQuery.active == 0")
        )
    except:
        driver.refresh()


def fetch_data():
    log.info("Fetching store_locator data")
    driver = SgSelenium().chrome()
    soup = pull_content(LOCATION_URL)
    page_urls = soup.find_all("a", {"class": "location__postlink"})
    for row in page_urls:
        page_url = row["href"]
        driver.get(page_url)
        log.info("Pull content => " + page_url)
        wait_load(driver)
        content = bs(driver.page_source, "lxml")
        temp_closed = (
            content.find("div", {"class": "title-banner"})
            .find("div", {"class": "info"})
            .find("div", {"class": "row"})
            .get_text(strip=True, separator=",")
        )
        if re.search(r"temporarily closed|has closed", temp_closed):
            continue
        location_name = row.find("span", {"class": "location__title"}).text.strip()
        info = content.find("script", {"class": "yext-schema-json"})
        if not info:
            raw_address = content.find("a", {"class": "direction"})["href"].replace(
                "https://maps.google.com/?daddr=", ""
            )
            street_address, city, state, zip_postal = getAddress(raw_address)
            latlong = json.loads(
                content.find("script", {"id": "gmw-map-js-extra"})
                .string.replace("var gmwMapObjects = ", "")
                .replace("};", "}")
            )
            phone = content.find("a", {"class": "number"}).text.strip()
            latitude = latlong["unik"]["locations"][0]["lat"]
            longitude = latlong["unik"]["locations"][0]["lng"]
        else:
            info = json.loads(info.string)
            street_address = info["address"]["streetAddress"]
            city = info["address"]["addressLocality"]
            state = info["address"]["addressRegion"]
            zip_postal = info["address"]["postalCode"]
            phone = info["telephone"]
            latitude = info["geo"]["latitude"]
            longitude = info["geo"]["longitude"]
        hours_of_operation = (
            content.find("h5", text="Studio Hours")
            .find_next("p")
            .get_text(strip=True, separator=",")
        )
        location_type = "unikwax"
        country_code = "US"
        store_number = MISSING
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
    driver.quit()


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
