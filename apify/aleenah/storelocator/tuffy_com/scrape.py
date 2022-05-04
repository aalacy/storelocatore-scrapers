from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager

from sgscrape import simple_scraper_pipeline as sp
from sgscrape.pause_resume import CrawlStateSingleton
from sglogging import sglog
import ssl
from bs4 import BeautifulSoup
import time
import re

ssl._create_default_https_context = ssl._create_unverified_context
DOMAIN = "tuffy_com"
logger = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def get_states():
    states = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]

    return states


def get_driver(url, driver=None):
    if driver is not None:
        driver.quit()

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
    x = 0
    while True:
        x = x + 1
        try:
            driver = SgChrome(
                executable_path=ChromeDriverManager().install(),
                user_agent=user_agent,
                is_headless=True,
            ).driver()
            driver.get(url)
            break
        except Exception:
            driver.quit()
            if x == 5:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver


def parse(location, idx, coordinates, state, page_url):
    data = {}
    data["locator_domain"] = DOMAIN
    data["location_name"] = location.h2.next_element.next_element.next_element
    data["store_number"] = state + "_" + location.h2.span.text
    try:
        data["page_url"] = page_url
    except:
        data["page_url"] = "<MISSING>"

    data["location_type"] = "Store"
    data["street_address"] = location.address.text.strip().split("\n")[0]
    data["city"] = location.address.text.strip().split("\n")[1].strip().replace(",", "")
    data["state"] = (
        location.address.text.strip().split("\n")[2].strip().replace(",", "")
    )

    data["country_code"] = "US"
    data["zip_postal"] = location.address.text.strip().split("\n")[3].strip()
    data["phone"] = location.select_one("span.tel").text
    data["latitude"] = coordinates[idx][0]
    data["longitude"] = coordinates[idx][1]
    hoo = {}
    for day in location.select_one("div.schedule-holder").select("span.day_name"):
        hoo[day.text.strip()] = day.next_element.next_element.strip()

    data["hours_of_operation"] = ", ".join(
        [key + ": " + value for key, value in hoo.items()]
    )
    data["raw_address"] = ", ".join(
        filter(
            None,
            [
                data["street_address"],
                data["city"],
                data["state"],
                data["zip_postal"],
                data["country_code"],
            ],
        )
    )
    return data


def fetch_data():

    states = get_states()
    logger.info(f"Total States to crawl: {len(states)}")

    for state in states:
        page_url = f"https://www.tuffy.com/location_search?zip_code={state}"
        try:
            driver = get_driver(page_url, driver=None)
        except Exception:
            driver = get_driver(page_url)

        logger.info(page_url)
        time.sleep(70)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        coordinates = coordinates = re.findall(
            r"LatLng\((\d+.\d+), (-?\d+.\d+)\)", str(soup)
        )[1:]
        if len(coordinates) == 0:
            time.sleep(60)
            continue

        locations = soup.select("div.contact-info")
        logger.info(f"{state} Locations Found: {len(locations)}")
        for idx, location in enumerate(locations):
            data = parse(location, idx, coordinates, state, page_url)
            yield data


def scrape():
    logger.info(f"Start Crawling {DOMAIN} ...")
    CrawlStateSingleton.get_instance().save(override=True)
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(DOMAIN),
        page_url=sp.MappingField(mapping=["page_url"], is_required=False),
        location_name=sp.MappingField(mapping=["location_name"]),
        latitude=sp.MappingField(mapping=["latitude"], part_of_record_identity=True),
        longitude=sp.MappingField(mapping=["longitude"], part_of_record_identity=True),
        street_address=sp.MappingField(mapping=["street_address"], is_required=False),
        city=sp.MappingField(mapping=["city"], is_required=False),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MappingField(mapping=["zip_postal"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"], is_required=False),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(mapping=["store_number"], is_required=False),
        hours_of_operation=sp.MappingField(
            mapping=["hours_of_operation"], is_required=False
        ),
        location_type=sp.MappingField(mapping=["location_type"], is_required=False),
        raw_address=sp.MappingField(mapping=["raw_address"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
