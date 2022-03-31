from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4
from sgzip.dynamic import DynamicGeoSearch

from sgselenium import SgChrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import ssl
import json

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")


def fetch_data():
    with SgChrome() as driver:
        driver.get("https://www.radissonhotels.com/en-us/destination")
        locator = WebDriverWait(driver, 10).until(  # noqa
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    "/html/body/main/section/div/div/div/div/p/p/a",
                )
            )
        )  # noqa
        time.sleep(15)
        time.sleep(5)
        reqs = list(driver.requests)
        logzilla.info(f"Length of driver.requests: {len(reqs)}")
        for r in reqs:
            x = r.url
            logzilla.info(x)
            if "zimba" in x and "hotels?" in x:
                son = json.loads(r.response.body)
    


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(
            mapping=["host"],
        ),
        page_url=sp.MissingField(),
        location_name=sp.MappingField(
            mapping=["name"],
            is_required=False,
            part_of_record_identity=True,
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
            is_required=False,
            part_of_record_identity=True,
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
            is_required=False,
            part_of_record_identity=True,
        ),
        street_address=sp.MappingField(
            mapping=["address"],
            part_of_record_identity=True,
        ),
        city=sp.MappingField(mapping=["city"], is_required=False),
        state=sp.MappingField(mapping=["neighborhood"], is_required=False),
        zipcode=sp.MappingField(mapping=["cep"], is_required=False),
        country_code=sp.MappingField(mapping=["country"], is_required=False),
        phone=sp.MissingField(),
        store_number=sp.MappingField(
            mapping=["_id"],
            is_required=False,
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MissingField(),
        location_type=sp.MappingField(mapping=["active"], is_required=False),
        raw_address=sp.MissingField(),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=10,
        duplicate_streak_failure_factor=-1,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
