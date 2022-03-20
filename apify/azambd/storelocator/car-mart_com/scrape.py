from bs4 import BeautifulSoup as bs
from sgselenium.sgselenium import SgChrome
from sglogging import sglog
from sgpostal.sgpostal import parse_address_usa
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import time
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
MISSING = "<MISSING>"
DOMAIN = "car-mart.com"
website = "https://www.car-mart.com"
log = sglog.SgLogSetup().get_logger(DOMAIN)

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)

week_first_day = "Monday"
weekend1 = "Saturday"
weekend2 = "Sunday"


def get_address(raw_address):
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


def fetch_data(driver):
    driver.get("https://www.car-mart.com/locations/")
    time.sleep(15)
    htmlpage = driver.page_source
    soup = bs(htmlpage, "html.parser")
    nodes = soup.findAll("div", class_="loc")
    for node in nodes[0:-1]:
        store_number = node["data-lotid"]
        latitude = node["data-lat"]
        longitude = node["data-lng"]
        location_name = node.find("span").text
        page_link = node.find("a")["href"]
        page_url = f"{website}{page_link}"
        phone = node.find("div", class_="info").find_all("p")[1].text
        raw_address = str(node.find("div", class_="info").find("p")).replace(
            "<br/>", " "
        )
        street_address, city, state, zip_postal = get_address(raw_address)
        street_address = street_address.replace("</A></P>", "").replace(">", "").strip()
        raw_address = f"{street_address}, {city}, {state} {zip_postal}".replace(
            MISSING, ""
        )
        hours_of_operation = (
            f"{week_first_day} - {weekend1} 9 AM - 6 PM; {weekend2} Closed"
        )

        yield SgRecord(
            locator_domain=DOMAIN,
            store_number=store_number,
            page_url=page_url,
            location_name=location_name,
            location_type=MISSING,
            street_address=street_address,
            city=city,
            zip_postal=zip_postal,
            state=state,
            country_code="US",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )


def scrape():
    log.info(f"Start Crawling {website} ...")
    start = time.time()
    count = 0
    with SgChrome(is_headless=True, user_agent=user_agent) as driver:
        with SgWriter(
            deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)
        ) as writer:
            for rec in fetch_data(driver):
                writer.write_row(rec)
                count = count + 1
    end = time.time()
    log.info(f"Total Rows Added= {count}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
