from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MultiMappingField
import json
from sglogging import sglog
from sgselenium import SgFirefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time


def fetch_data():
    url = "https://stores.sleepoutfitters.com/"
    logzilla = sglog.SgLogSetup().get_logger(logger_name="sleepoutfitter")
    son = []
    with SgFirefox() as driver:
        logzilla.info(f"Opening {url}")  # noqa
        driver.get(url)
        logzilla.info(f"Waiting for requests to load")  # noqa
        time.sleep(5)
        footer = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="sls-locations-list-scroller"]/footer/nav')
            )
        )
        # https://stackoverflow.com/questions/53571352/how-to-scroll-down-on-my-page-through-selenium-and-python
        driver.execute_script("return arguments[0].scrollIntoView(true);", footer)
        time.sleep(3)
        driver.execute_script("return arguments[0].scrollIntoView(true);", footer)
        time.sleep(3)
        driver.execute_script("return arguments[0].scrollIntoView(true);", footer)
        time.sleep(3)
        driver.execute_script("return arguments[0].scrollIntoView(true);", footer)
        time.sleep(3)
        driver.execute_script("return arguments[0].scrollIntoView(true);", footer)
        time.sleep(5)
        logzilla.info(f"Looking for API calls")  # noqa
        for r in driver.requests:
            if "locations-details" in r.path:
                try:
                    son.append(json.loads(r.response.body))
                except Exception:
                    continue

    for i in son:
        for j in i["features"]:
            yield j

    logzilla.info(f"Finished grabbing data!!")  # noqa


def pretty_hours(x):
    x = (
        x.replace("]]", "; ")
        .replace("'", "")
        .replace("[", "")
        .replace("]", "")
        .replace(",", "")
        .replace("}", "")
        .replace("{", "")
    )
    return x


def fix_address(x):
    x = x.replace("None", "")
    h = []
    for i in x.split(","):
        if len(i) > 2:
            h.append(i)
    return ", ".join(h)


def scrape():
    url = "https://stores.sleepoutfitters.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(
            mapping=["properties", "slug"], value_transform=lambda x: url + x
        ),
        location_name=MappingField(mapping=["properties", "name"]),
        latitude=MappingField(mapping=["geometry", "coordinates", 1]),
        longitude=MappingField(mapping=["geometry", "coordinates", 0]),
        street_address=MultiMappingField(
            mapping=[["properties", "addressLine1"], ["properties", "addressLine2"]],
            multi_mapping_concat_with=", ",
            value_transform=fix_address,
        ),
        city=MappingField(mapping=["properties", "city"]),
        state=MappingField(mapping=["properties", "province"]),
        zipcode=MappingField(mapping=["properties", "postalCode"]),
        country_code=MappingField(mapping=["properties", "country"]),
        phone=MappingField(mapping=["properties", "phoneNumber"]),
        store_number=MappingField(
            mapping=["properties", "id"], part_of_record_identity=True
        ),
        hours_of_operation=MappingField(
            mapping=["properties", "hoursOfOperation"], value_transform=pretty_hours
        ),
        location_type=MappingField(
            mapping=["properties", "isPermanentlyClosed"],
            value_transform=lambda x: "<MISSING>"
            if x == "False"
            else "isPermanentlyClosed",
        ),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="sleepoutfitters.com",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )
    pipeline.run()


if __name__ == "__main__":
    scrape()
