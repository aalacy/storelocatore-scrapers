from bs4 import BeautifulSoup as bs

from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from sgscrape import simple_scraper_pipeline as sp

from sglogging import sglog
import json
import re
import ssl
import time

ssl._create_default_https_context = ssl._create_unverified_context

DOMAIN = "spring-market.com"
website = "https://www.spring-market.com"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def get_driver(url, driver=None):
    if driver is not None:
        driver.quit()

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
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
            time.sleep(60)
            break
        except Exception:
            driver.quit()
            if x == 2:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver


def fetch_data():

    x = 0
    while True:
        x = x + 1

        url = "https://www.spring-market.com/sm/planning/rsid/713/store"
        if x == 1:
            driver = get_driver(url)
        else:
            driver = get_driver(url, driver=driver)
        soup = bs(driver.page_source, "html.parser")
        grids = json.loads(
            (
                soup.find(
                    "script", string=re.compile("window.__PRELOADED_STATE__=")
                ).string.replace("window.__PRELOADED_STATE__=", "")
            )
        )

        log.info(f'Total Locations: {len(grids["stores"]["allStores"]["items"])}')
        if len(grids) == 0:
            continue
        else:
            break

    for grid in grids["stores"]["allStores"]["items"]:
        location_name = grid["name"]
        log.info(f"Location Name: {location_name}")
        store_number = grid["retailerStoreId"]
        street_address = grid["addressLine1"]
        city = grid["city"]
        state = grid["countyProvinceState"]
        zip_postal = grid["postCode"]
        latitude = grid["location"]["latitude"]
        longitude = grid["location"]["longitude"]
        log.info(f"Store Number: {store_number}")
        phone = grid["phone"]
        hours_of_operation = grid["openingHours"].replace("\n", "")
        location_type = "<MISSING>"
        page_url = "https://www.spring-market.com/sm/planning/rsid/713/store"
        country_code = "US"

        yield {
            "locator_domain": DOMAIN,
            "page_url": page_url,
            "location_name": location_name,
            "latitude": latitude,
            "longitude": longitude,
            "city": city,
            "store_number": store_number,
            "street_address": street_address,
            "state": state,
            "zip": zip_postal,
            "phone": phone,
            "location_type": location_type,
            "hours": hours_of_operation,
            "country_code": country_code,
        }


def scrape():
    log.info(f"Start Crawling {website} ...")
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"]),
        page_url=sp.MappingField(mapping=["page_url"], is_required=False),
        location_name=sp.MappingField(
            mapping=["location_name"],
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
        ),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], is_required=False
        ),
        city=sp.MappingField(mapping=["city"], is_required=False),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MultiMappingField(mapping=["zip"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"]),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(
            mapping=["store_number"], part_of_record_identity=True
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"], is_required=False),
        location_type=sp.MappingField(mapping=["location_type"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )
    pipeline.run()


scrape()
