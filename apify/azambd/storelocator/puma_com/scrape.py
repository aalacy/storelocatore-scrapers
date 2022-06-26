from sgrequests import SgRequests
from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
import json
from sgselenium import SgChrome
from selenium.webdriver.common.by import By
import time
import ssl
import pycountry
from lxml import html

ssl._create_default_https_context = ssl._create_unverified_context

DOMAIN = "puma.com"
logger = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

STORE_JSON_URL = (
    "https://about.puma.com/api/PUMA/Feature/Locations/StoreLocator/StoreLocator"
)
MISSING = "<MISSING>"
http = SgRequests()


def do_fuzzy_search(country):
    try:
        result = pycountry.countries.search_fuzzy(country)
    except Exception:
        return MISSING
    else:
        return result[0].alpha_2


def get_var_name(value):
    try:
        return int(value)
    except ValueError:
        pass
    return value


def get_json_objectVariable(Object, varNames, noVal=MISSING):
    value = noVal
    for varName in varNames.split("."):
        varName = get_var_name(varName)
        try:
            value = Object[varName]
            Object = Object[varName]
        except Exception:
            return noVal
    return value


def fetch_single_store(countryjson, page_url, retry=0):
    try:
        if "ROMANIA_EEMEA" in str(countryjson):
            countryjson = "ROMANIA"
        if "Lithuanta" in str(countryjson):
            countryjson = "Lithuania"

        country_code = do_fuzzy_search(countryjson)
        logger.info(f"Crawling {page_url} ...")
        response = http.get(page_url)
        body = html.fromstring(response.text, "lxml")

        data = body.xpath('//script[contains(@id, "current-store-details")]/text()')
        if len(data) == 0:
            storeData = {}
        else:
            storeData = json.loads(data[0])

        street_address = get_json_objectVariable(storeData, "address.streetAddress")

        hours = get_json_objectVariable(storeData, "openingHoursSpecification", [])
        hoo = []
        for hour in hours:
            hoo.append(
                f"{hour['dayOfWeek']}: {hour['opens']} - {hour['closes']}".replace(
                    "http://schema.org/", ""
                )
            )

        hoo = "; ".join(hoo)
        return country_code, street_address, hoo
    except Exception as e:
        if retry > 3:
            try:
                logger.error(f"Error loading {page_url}, message={e}")
            except Exception as e1:
                logger.error(f"Error , message={e1}")
                pass
            return None
        else:
            return fetch_single_store(countryjson, page_url, retry + 1)


def parse_json(store):
    data = {}
    data["locator_domain"] = DOMAIN
    data["store_number"] = store["StoreId"]
    data["page_url"] = "https://about.puma.com" + store["Url"]
    data["location_name"] = store["StoreName"]
    data["location_type"] = "Outlet" if "Outlet" in data["location_name"] else "Store"
    data["city"] = store["City"]
    data["state"] = store["State"]
    if data["state"] is None:
        data["state"] = MISSING
    countryjson = store["Country"]
    data["zip_postal"] = store["PostalCode"]
    data["phone"] = store["PhoneNumber"]
    data["latitude"] = store["Lat"]
    data["longitude"] = store["Lng"]

    (
        data["country_code"],
        data["street_address"],
        data["hours_of_operation"],
    ) = fetch_single_store(countryjson, data["page_url"])
    if "None" in str(data["hours_of_operation"]):
        data["hours_of_operation"] = ""

    return data


def fetch_data():
    with SgChrome() as driver:
        driver.get(STORE_JSON_URL)
        time.sleep(15)
        data_json = json.loads(
            driver.find_element(by=By.CSS_SELECTOR, value="body").text
        )
        logger.info(f'Total Stores: {len(data_json["StoreLocatorItems"])}')
        for store in data_json["StoreLocatorItems"]:
            yield parse_json(store)


def scrape():
    logger.info(f"Start Crawling {DOMAIN} ...")
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(DOMAIN),
        page_url=sp.MappingField(mapping=["page_url"], part_of_record_identity=True),
        location_name=sp.MappingField(mapping=["location_name"]),
        latitude=sp.MappingField(mapping=["latitude"]),
        longitude=sp.MappingField(mapping=["longitude"]),
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
