from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
import ssl
import json
from lxml import html

session = SgRequests()
ssl._create_default_https_context = ssl._create_unverified_context
MISSING = "<MISSING>"
DOMAIN = "chocolatsfavoris.com"
logger = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
page_url = "https://www.chocolatsfavoris.com/stores"
class_name = "page__container__content"


def fetch_page_from_driver(url, class_name, driver=None):
    if driver is not None:
        driver.quit()

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36"
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

            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            break
        except Exception:
            driver.quit()
            if x == 3:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver.page_source


def get_var_name(value):
    try:
        return int(value)
    except ValueError:
        pass
    return value


def get_JSON_object_variable(Object, varNames, noVal=MISSING):
    value = noVal
    for varName in varNames.split("."):
        varName = get_var_name(varName)
        try:
            value = Object[varName]
            Object = Object[varName]
        except Exception:
            return noVal
    return value


def get_address(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_intl(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode
            country_code = data.country

            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            if country_code is None or len(country_code) == 0:
                country_code = MISSING

            return street_address, city, state, zip_postal, country_code
    except Exception as e:
        logger.info(f"No valid address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def parse_json(details, location):
    data = {}
    data["locator_domain"] = DOMAIN
    data["location_name"] = location["name"]
    data["store_number"] = location["placeId"]

    data["page_url"] = page_url
    data["location_type"] = MISSING
    raw_address = get_JSON_object_variable(details, "formatted_address")
    street_address, city, state, zip_postal, country_code = get_address(raw_address)
    data["street_address"] = street_address
    data["city"] = city
    data["state"] = state
    data["country_code"] = country_code
    data["zip_postal"] = zip_postal
    data["phone"] = get_JSON_object_variable(details, "formatted_phone_number")
    data["latitude"] = location["position"]["lat"]
    data["longitude"] = location["position"]["lng"]
    data["raw_address"] = raw_address
    data["hours_of_operation"] = "; ".join(
        get_JSON_object_variable(details, "opening_hours.weekday_text", [])
    )

    return data


def fetch_data():
    htmlpage = fetch_page_from_driver(page_url, class_name, driver=None)
    api_key = htmlpage.split("apiKey: '")[1].split("'")[0].strip()
    body = html.fromstring(htmlpage, "lxml")
    nodes = body.xpath(
        "//div[@data-react-class='ReactComponents.StoreMap']/@data-react-props"
    )[0]
    locations = json.loads(nodes)["stores"]
    logger.info(f"Total stores: {len(locations)}")
    count = 0
    for location in locations:
        count = count + 1
        logger.info(f"{count}. scrapping {location['name']}: {location['placeId']} ...")
        response = session.get(
            f"https://maps.googleapis.com/maps/api/place/details/json?place_id={location['placeId']}&key={api_key}"
        )
        details = json.loads(response.text)["result"]

        i = parse_json(details, location)
        yield i


def scrape():
    logger.info(f"Start Crawling {DOMAIN} ...")
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(DOMAIN),
        page_url=sp.MappingField(mapping=["page_url"], is_required=False),
        location_name=sp.MappingField(mapping=["location_name"]),
        latitude=sp.MappingField(mapping=["latitude"]),
        longitude=sp.MappingField(mapping=["longitude"]),
        street_address=sp.MappingField(mapping=["street_address"], is_required=False),
        city=sp.MappingField(mapping=["city"], is_required=False),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MappingField(mapping=["zip_postal"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"], is_required=False),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(
            mapping=["store_number"], part_of_record_identity=True
        ),
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
