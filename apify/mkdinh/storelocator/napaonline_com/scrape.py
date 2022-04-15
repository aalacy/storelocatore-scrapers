import re
import json
from random import randint
from time import sleep
from bs4 import BeautifulSoup as bs
from datetime import datetime as dt
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgselenium.sgselenium import SgChrome
from concurrent.futures import ThreadPoolExecutor, as_completed
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries
from tenacity import retry, stop_after_attempt
from sgzip.static import static_zipcode_list
from sgscrape.sgpostal import parse_address, USA_Best_Parser

logger = SgLogSetup().get_logger("napaonline_com")
user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0"
)
base_url = "https://www.napaonline.com/stores"


def get_driver():
    driver = SgChrome(
        is_headless=True, seleniumwire_auto_config=True, user_agent=user_agent
    ).driver()
    driver.set_script_timeout(600)
    load_initial_page(driver)

    return driver


def fetch(postal, driver, retry=0):
    try:
        sleep(randint(2, 5))
        html = driver.execute_async_script(
            f"""
            fetch('https://www.napaonline.com/en/store-finder?q={postal}&sort=true&page=50')
                .then(res => res.text())
                .then(arguments[0])
        """
        )

        return bs(html, "html.parser")
    except Exception as e:
        logger.error(e)
        if retry < 5:
            return fetch(postal, driver, retry + 1)

        return None


def get(entity, key, default=SgRecord.MISSING):
    return entity.get(key, default)


def get_hours(store_number, soup):
    hours = []
    store_hours = soup.find(
        "li", class_="aadata-store-item", attrs={"data-storeid": store_number}
    ).find_all("div", class_="store-hours-block")
    for hour in store_hours:
        day = hour.find("span", class_="days").text.strip()
        hour_of_operation = hour.find("span", class_="hours").text.strip()
        hours.append(f"{day} {hour_of_operation}")

    return ", ".join(hours)


@retry(stop=stop_after_attempt(3), reraise=True)
def load_initial_page(driver):
    sleep(randint(2, 5))
    driver.get("http://www.napaonline.com/store-locator")
    sleep(20)


def fetch_locations(postal, driver, writer):
    soup = fetch(postal, driver)

    if not soup:
        return

    canvas = soup.find("div", id="map_canvas")

    if not canvas:
        return

    locations = json.loads(canvas.attrs["data-stores"])
    for _, location in locations.items():
        locator_domain = "napaonline.com"
        store_number = location["facilityId"]
        page_url = location["url"]
        if "https://www.napaonline.com" not in page_url:
            page_url = f"https://www.napaonline.com{page_url}"

        location_name = location["name"]

        cleaned = re.split("<br/>", location["address"])
        phone = cleaned.pop()
        cleaned = [item for item in cleaned if item]
        address = re.sub("<br/>|&nbsp", " ", " ".join(cleaned))

        parsed = parse_address(USA_Best_Parser(), address)

        street_address = parsed.street_address_1
        city = parsed.city
        state = parsed.state
        postal = parsed.postcode
        country_code = parsed.country

        latitude = location["latitude"]
        longitude = location["longitude"]

        hours_of_operation = get_hours(store_number, soup)

        writer.write_row(
            SgRecord(
                locator_domain=locator_domain,
                location_name=location_name,
                store_number=store_number,
                page_url=page_url,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
        )


def fetch_data():
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=100
        )
    ) as writer, ThreadPoolExecutor(max_workers=4) as executor, get_driver() as driver:
        search = static_zipcode_list(country_code=SearchableCountries.USA, radius=5)
        futures = [
            executor.submit(fetch_locations, postal, driver, writer)
            for postal in search
        ]
        for future in as_completed(futures):
            pass


def scrape():
    now = dt.now()
    fetch_data()
    logger.info(f"duration: {dt.now() - now}")


if __name__ == "__main__":
    scrape()
