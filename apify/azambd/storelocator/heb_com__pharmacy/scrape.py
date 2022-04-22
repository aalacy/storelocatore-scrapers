from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
from bs4 import BeautifulSoup as bs
from sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import re
import ssl


DOMAIN = "heb.com"
logger = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

ssl._create_default_https_context = ssl._create_unverified_context


api_url = "https://www.heb.com/storelocator/storelocator_ajax.jsp?lat=29.39799&lon=-98.51485&radius=10000&postalCode=78204-2427&view=&selectedFeatures=1107~"

class_name = "storelocator-store-list "


def get_driver(url, class_name, driver=None):
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

            WebDriverWait(driver, 20).until(
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
    return driver


def parse(location):
    data = {}
    data["locator_domain"] = "heb.com"
    data["location_name"] = location.select_one("h3.store-card__name").text.strip()
    data["store_number"] = location.select_one("button")["name"]
    data["page_url"] = (
        "https://www.heb.com" + location.select_one("a.store-card__action")["href"]
    )
    data["location_type"] = "Pharmacy"
    data["street_address"] = location.select_one("span.store-card__street").text
    data["city"] = location.select_one("span[itemprop=addressLocality]").text
    data["state"] = location.select_one("span[itemprop=addressRegion]").text
    data["country_code"] = "US"
    data["zip_postal"] = location.select_one("span[itemprop=postalCode]").text
    data["phone"] = location.select_one("p[itemtype*=Pharmacy]").a["content"]
    data["latitude"] = re.findall(r"(\d+.\d+,-\d+.\d+)", location.script.text)[1].split(
        ","
    )[0]
    data["longitude"] = re.findall(r"(\d+.\d+,-\d+.\d+)", location.script.text)[
        1
    ].split(",")[1]
    data["hours_of_operation"] = ", ".join(
        loc.text.strip()
        for loc in location.select_one("p[itemtype*=Pharmacy]")
        .find_next("p")
        .contents[2::2]
    )
    data["raw_address"] = ", ".join(
        [
            data["street_address"],
            data["city"],
            data["state"],
            data["zip_postal"],
            data["country_code"],
        ]
    )

    return data


def fetch_data():
    try:
        driver = get_driver(api_url, class_name, driver=None)
    except Exception:
        driver = get_driver(api_url, class_name)

    soup = bs(driver.page_source, "lxml")
    locations = soup.select("li.storelocator_store")
    for location in locations:

        if location.select_one("p[itemtype*=Pharmacy]") is None:
            continue

        data = parse(location)
        yield data


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
        raw_address=sp.MappingField(mapping=["raw_address"]),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=1,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
