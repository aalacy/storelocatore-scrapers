from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
from sgselenium import SgSelenium
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

DOMAIN = "speedwell-pharmacy.co.uk"
BASE_URL = "https://speedwell-pharmacy.co.uk"
LOCATION_URL = "https://speedwell-pharmacy.co.uk/manor-pharmacy-group"
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


def load_page(driver, url):
    try:
        driver.get(url)
        driver.implicitly_wait(10)
        hoo_content = driver.find_element_by_css_selector("div#bs-12 span")
        driver.execute_script("arguments[0].scrollIntoView();", hoo_content)
        hoo_content.click()
    except:
        driver.refresh()
        return load_page(driver, url)
    return bs(driver.page_source, "lxml")


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    driver = SgSelenium().chrome()
    contents = soup.select("div[data-ux='ContentCards'] a")
    for row in contents:
        page_url = BASE_URL + row["href"]
        log.info("Pull content => " + page_url)
        store = load_page(driver, page_url)
        content_parent = row.parent.parent
        location_name = content_parent.find("h4", {"role": "heading"}).text.strip()
        try:
            raw_address = (
                store.select_one(
                    "div.widget-content-content-1 section[data-ux='Section']"
                )
                .find("span", text=re.compile(r"Address.*"))
                .text.replace("\n", "")
                .strip()
            )
        except:
            raw_address = (
                content_parent.find("div", {"data-ux": "ContentCardText"})
                .find("p")
                .text.replace("\n", "")
                .strip()
            )
        street_address, city, state, zip_postal = getAddress(raw_address)
        phone = store.find(
            re.compile(r"span|p"), text=re.compile(r"Telephone:.*|Tel:.*")
        )
        if not phone:
            phone = store.find("a", {"href": re.compile(r"tel:.*")}).text.strip()
        else:
            phone = phone.text.replace("Telephone:", "").replace("Tel:", "").strip()
        country_code = "UK"
        store_number = MISSING
        hours_of_operation = (
            store.find("div", {"data-aid": "CONTACT_HOURS_REND"})
            .find("table")
            .get_text(strip=True, separator=" ")
        )
        location_type = MISSING
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
    driver.quit()


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
