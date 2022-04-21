from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager

from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
import ssl
import json
from bs4 import BeautifulSoup

ssl._create_default_https_context = ssl._create_unverified_context

DOMAIN = "napacanada.com"

logger = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


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
            break
        except Exception:
            driver.quit()
            if x == 5:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver


def get_all_stores():
    driver = get_driver("https://www.napacanada.com/en/auto-parts-stores-near-me")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    provinces = [
        "https://www.napacanada.com" + province["href"]
        for province in soup.select("a[href*=auto-parts-stores-near-me]")[:-1]
    ]
    urls = []
    for province in provinces:
        logger.info(f"Crawling Province: {province}")
        driver.get(province)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        for url in soup.select("a[href*=auto-parts-stores-near-me]")[1:-1]:
            urls.append("https://www.napacanada.com" + url["href"])
    return driver, urls


def get_missed_cities(MISSED_CITIES):
    """
    Find and get broken store links.
    """
    new_links = []
    for link in MISSED_CITIES:
        CITY = link.split("/")[-1].title()
        driver = get_driver(
            f"https://www.napacanada.com/en/store-finder?q={CITY}&page=10"
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")
        for store in soup.select("li.aadata-store-item"):
            new_links.append("https://www.napacanada.com" + store.a["href"])
    return new_links


def parse(location):
    data = {}

    data["locator_domain"] = DOMAIN
    data["location_name"] = location["name"]
    data["store_number"] = location["@id"]
    data["page_url"] = location["url"]
    data["location_type"] = location["@type"]
    data["street_address"] = location["address"]["streetAddress"]
    data["city"] = location["address"]["addressLocality"]
    data["state"] = location["address"]["addressRegion"]
    data["country_code"] = location["address"]["addressCountry"]
    data["zip_postal"] = location["address"]["postalCode"]
    data["phone"] = location["telephone"]
    data["latitude"] = location["geo"]["latitude"]
    data["longitude"] = location["geo"]["longitude"]

    hoo = []
    for day in location["openingHoursSpecification"]:
        hoo.append(day["dayOfWeek"][0] + ": " + day["opens"] + "-" + day["closes"])
    hoo = ", ".join(hoo)

    data["hours_of_operation"] = hoo
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

    driver, urls = get_all_stores()
    logger.info(f"Total pages to crawl: {len(urls)}")
    MISSED_CITIES = []
    for url in urls:
        logger.info(f"Crawling {url}")
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        try:
            location = json.loads(soup.select("script[type*=application]")[1].text)
        except Exception as e:
            logger.info(f"BROKEN LINK {url}: {e}")
            MISSED_CITIES.append(url)
            continue
        data = parse(location)
        yield data

    missed_links = get_missed_cities(MISSED_CITIES)
    for url in missed_links:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        location = json.loads(soup.select("script[type*=application]")[1].text)
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
