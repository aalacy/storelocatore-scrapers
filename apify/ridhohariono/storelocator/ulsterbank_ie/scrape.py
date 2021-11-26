from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgselenium import SgSelenium
from sgscrape.sgpostal import parse_address_intl
import re
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


DOMAIN = "ulsterbank.ie"
LOCATION_URL = "https://locator.ulsterbank.ie"
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


def fetch_data():
    log.info("Fetching store_locator data")
    driver = SgSelenium().chrome()
    driver.get(LOCATION_URL)
    driver.implicitly_wait(10)
    try:
        driver.find_element_by_id("onetrust-accept-btn-handler").click()
    except:
        pass
    driver.execute_script(
        "return document.getElementsByClassName('bl-captcha')[0].remove();"
    )
    driver.execute_script("return document.getElementById('maxMiles').value = '10000'")
    driver.execute_script(
        "return document.getElementById('listSizeInNumbers').value = '10000'"
    )
    driver.find_element_by_id("search-input").send_keys("Ireland")
    driver.find_element_by_id("search-button").click()
    driver.implicitly_wait(10)
    contents = bs(driver.page_source, "lxml").select("div.results-marker-link")
    driver.quit()
    for row in contents:
        page_url = LOCATION_URL + row.find("a")["href"]
        store = pull_content(page_url)
        location_name = (
            store.find("div", id="single-result-header")
            .find("div", {"class": "header left"})
            .text.strip()
        )
        table = store.find("table", id="results-table")
        table.find("tr").decompose()
        info = (
            table.get_text(strip=True, separator="@@")
            .replace("@@Customer support centre:", "")
            .split("@@")
        )
        raw_address = ",".join(info[:3]).strip()
        street_address, city, state, zip_postal = getAddress(raw_address)
        phone = info[3].replace("Personal: ", "").strip()
        country_code = "IE"
        hoo = ""
        for hday in table.find_all("tr", {"class": "time"}):
            hoo += hday.get_text(strip=True, separator=" ").strip() + ","
        hours_of_operation = hoo.rstrip(",")
        location_type = "BRANCH"
        store_number = re.sub(r"\D+", "", location_name)
        latlong = (
            store.find("a", {"class": "email-location"})["href"]
            .split("maps?q=")[1]
            .split(",")
        )
        latitude = latlong[0]
        longitude = latlong[0]
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
            raw_address=raw_address,
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
