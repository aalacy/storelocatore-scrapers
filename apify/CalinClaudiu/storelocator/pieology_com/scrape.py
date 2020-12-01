from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
import json
from sglogging import sglog
from sgselenium import SgFirefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def fetch_data():

    url = "https://order.pieology.com/locations"

    logzilla = sglog.SgLogSetup().get_logger(logger_name="Crawler")
    son = "Initializing geckodriver"
    logzilla.info(f"{son}")
    with SgFirefox() as driver:
        son = "Getting page"
        logzilla.info(f"{son}")
        driver.get("https://pieology.com/")
        driver.get(url)
        son = "Waiting for page to load"
        logzilla.info(f"{son}")
        items = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="root"]/div/main/div/div[2]/div')
            )
        )
        for r in driver.requests:
            if "/api/vendors/regions" in r.path:
                states = json.loads(r.response.body)
                logzilla.info(f"Found {len(states)} states with locations\n\n")
        for i in states:
            logzilla.info(f'\n\nGrabbing locations from {i["name"]}.')
            son = "Getting page"
            logzilla.info(f"{son}")
            driver.get("https://order.pieology.com/locations/" + i["code"])
            son = "Waiting for page to load"
            logzilla.info(f"{son}")
            stores = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//*[@id="root"]/div/main/div/div[1]/div[2]/div/a')
                )
            )
            for r in driver.requests:
                if ("/api/vendors/search/" + i["code"]) in r.path:
                    data = json.loads(r.response.body)
                    logzilla.info(
                        f'Found {len(data["vendor-search-results"])} stores in {i["name"]}.'
                    )
                    for loc in data["vendor-search-results"]:
                        yield loc
    son = "Finished grabbing data!!"
    logzilla.info(f"{son}")


def pretty_hours(k):
    h = []
    for i in k:
        h.append(str(i["weekDay"]) + ": " + str(i["description"]))

    return "; ".join(h)


def scrape():
    url = "https://pieology.com"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(
            mapping=["slug"],
            value_transform=lambda x: "https://order.pieology.com/menu/"
            + str(x)
            + "?showInfoModal=true",
        ),
        location_name=MappingField(mapping=["name"]),
        latitude=MappingField(mapping=["latitude"]),
        longitude=MappingField(mapping=["longitude"]),
        street_address=MappingField(mapping=["streetAddress"]),
        city=MappingField(mapping=["city"]),
        state=MappingField(mapping=["state"]),
        zipcode=MappingField(mapping=["address", "postalCode"]),
        country_code=MappingField(mapping=["address", "country"]),
        phone=MappingField(mapping=["phoneNumber"]),
        store_number=MappingField(mapping=["id"]),
        hours_of_operation=MappingField(
            mapping=["weeklySchedule", "calendars", 0, "schedule"],
            raw_value_transform=pretty_hours,
        ),
        location_type=MappingField(mapping=["unavailableMessage"], is_required=False),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="pieology.com",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
