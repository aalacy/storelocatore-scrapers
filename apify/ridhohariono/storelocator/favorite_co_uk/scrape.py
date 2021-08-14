from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium import SgSelenium
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
import time
from sgscrape.sgpostal import parse_address_intl

DOMAIN = "favorite.com"
BASE_URL = "https://stores.favorite.com/"
LOCATION_URL = "https://favorite.co.uk/store-finder?delivery=0&lat={}&lng={}"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, sdch",
    "Accept-Language": "en-US,en;q=0.8",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()

MISSING = "<MISSING>"
CITIES = [
    "Aberdeen",
    "Armagh",
    "Bangor",
    "Bath",
    "Belfast",
    "Birmingham",
    "Bradford",
    "Brighton & Hove",
    "Bristol",
    "Cambridge",
    "Canterbury",
    "Cardiff",
    "Carlisle",
    "Chelmsford",
    "Chester",
    "Chichester",
    "Coventry",
    "Derby",
    "Derry",
    "Dundee",
    "Durham",
    "Edinburgh",
    "Ely",
    "Exeter",
    "Glasgow",
    "Gloucester",
    "Hereford",
    "Inverness",
    "Kingston upon Hull",
    "Lancaster",
    "Leeds",
    "Leicester",
    "Lichfield",
    "Lincoln",
    "Lisburn",
    "Liverpool",
    "London",
    "Manchester",
    "Newcastle upon Tyne",
    "Newport",
    "Newry",
    "Norwich",
    "Nottingham",
    "Oxford",
    "Perth",
    "Peterborough",
    "Plymouth",
    "Portsmouth",
    "Preston",
    "Ripon",
    "St Albans",
    "St Asaph",
    "St Davids",
    "Salford",
    "Salisbury",
    "Sheffield",
    "Southampton",
    "Stirling",
    "Stoke-on-Trent",
    "Sunderland",
    "Swansea",
    "Truro",
    "Wakefield",
    "Wells",
    "Westminster",
    "Winchester",
    "Wolverhampton",
    "Worcester",
    "York",
    "Sheerness",
    "Kilburn",
    "Yeovil",
    "Bethnal Green",
    "Corby",
    "Rayleigh",
    "Berkshire",
    "Sussex",
    "Buckinghamshire",
    "Essex",
    "Middlesex",
    "Heston",
    "Ipswich",
    "Croydon",
    "Greenleys",
    "Witham",
    "Crawley",
    "Stevenage",
    "Irthlingborough",
    "Hoddesdon",
    "Gravesend",
    "Felixstowe",
    "Dunstable",
    "Rainham",
    "Snodland",
]


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


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def parse_hours(table):
    data = table.find("tbody")
    days = data.find_all("td", {"class": "c-hours-details-row-day"})
    hours = data.find_all("td", {"class": "c-hours-details-row-intervals"})
    hoo = []
    for i in range(len(days)):
        hours_formated = "{}: {}".format(days[i].text, hours[i].text)
        hoo.append(hours_formated)
    return ", ".join(hoo)


def get_latlong(url):
    latlong = re.search(r"lat=(-?[\d]*\.[\d]*)\&lng=(-[\d]*\.[\d]*)", url)
    if not latlong:
        return "<MISSING>", "<MISSING>"
    return latlong.group(1), latlong.group(2)


def wait_load(driver):
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="findstore-postcode"]'))
        )
    except:
        driver.refresh()
    return driver


def fetch_data():
    log.info("Fetching store_locator data")
    driver = SgSelenium().chrome()
    driver.get(
        "https://favorite.co.uk/store-finder?postcode=london&delivery=0&lat=51.5073509&lng=-0.1277583"
    )
    for city in CITIES:
        driver = wait_load(driver)
        driver.find_element_by_xpath('//*[@id="findstore-postcode"]').clear()
        driver.find_element_by_xpath('//*[@id="findstore-postcode"]').send_keys(city)
        driver.find_element_by_xpath('//*[@id="findstore-submit"]').click()
        time.sleep(1)
        soup = bs(driver.page_source, "lxml")
        main = soup.find("div", {"class": "row row-store mb0"})
        if not main or len(main) > 50:
            continue
        for row in main:
            page_url = driver.current_url
            content = main.find("div", {"class": "col-12 mb0"})
            location_name = (
                content.find("div", {"class": "store-name"})
                .get_text(strip=True, separator=",")
                .split(",")[0]
            )
            raw_address = ", ".join(
                content.find("div", {"class": "store-name"})
                .get_text(strip=True, separator=",")
                .split(",")[2:]
            )
            street_address, city, state, zip_postal = getAddress(raw_address)
            country_code = "UK"
            store_number = "<MISSING>"
            phone = soup.find(
                "a", {"class": "store-no", "href": re.compile(r"tel\:\/\/.*")}
            )
            if not phone:
                phone = "<MISSING>"
            else:
                phone = phone.text
            day_hours = content.find("ul", {"class": "opening-times"}).find_all(
                "li", {"class": False}
            )
            hours = []
            for x in day_hours:
                hoo = x.find("span", {"class": "ot"}).text.strip()
                hours.append(hoo)
            if all(value == "Closed" for value in hours):
                location_type = "CLOSED"
            else:
                location_type = "OPEN"
            hours_of_operation = (
                ", ".join(
                    content.find("ul", {"class": "opening-times"})
                    .get_text(strip=True, separator=",")
                    .split(",")[1:]
                )
                .replace("Delivery, ", "")
                .strip()
            )
            latitude, longitude = get_latlong(page_url)
            log.info("Found Location{} => {}".format(location_name, street_address))
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
                raw_address=raw_address,
            )
            time.sleep(1)
    driver.quit()


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.PHONE,
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
