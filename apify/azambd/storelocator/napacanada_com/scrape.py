from sgselenium import SgFirefox

from sgscrape import simple_scraper_pipeline as sp
from sgscrape.pause_resume import CrawlStateSingleton
from sglogging import sglog
import ssl
import json
from bs4 import BeautifulSoup

ssl._create_default_https_context = ssl._create_unverified_context

DOMAIN = "napacanada.com"

logger = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def get_all_stores():
    with SgFirefox(block_javascript=False) as driver:

        driver.get_and_wait_for_request(
            "https://www.napacanada.com/en/auto-parts-stores-near-me"
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")
        provinces = [
            "https://www.napacanada.com" + province["href"]
            for province in soup.select("a[href*=auto-parts-stores-near-me]")[:-1]
        ]
        logger.info(f"Total provinces to crawl: {len(provinces)}")
        urls = []
        for province in provinces:
            logger.info(f"Crawling Province: {province}")
            driver.get_and_wait_for_request(province)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for url in soup.select("a[href*=auto-parts-stores-near-me]")[1:-1]:
                urls.append("https://www.napacanada.com" + url["href"])

    return urls


def get_missed_cities(MISSED_CITIES):
    """
    Find and get broken store links.
    """
    with SgFirefox(block_javascript=False) as driver:

        new_links = []

        for link in MISSED_CITIES:
            CITY = link.split("/")[-1].title()
            driver.get_and_wait_for_request(
                f"https://www.napacanada.com/en/store-finder?q={CITY}&page=10"
            )
            soup = BeautifulSoup(driver.page_source, "html.parser")
            for store in soup.select("li.aadata-store-item"):
                new_links.append("https://www.napacanada.com" + store.a["href"])

    return new_links


def parse(location):
    data = {}

    data["locator_domain"] = DOMAIN
    data["location_name"] = location["name"].replace("NAPA Auto Parts -", "").strip()
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
    with SgFirefox(block_javascript=False) as driver:

        urls = get_all_stores()
        logger.info(f"Total pages to crawl: {len(urls)}")
        MISSED_CITIES = []
        for url in urls:
            url = url.replace(" ", "%20")
            logger.info(f"Crawling {url}")
            driver.get_and_wait_for_request(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            try:
                location = json.loads(soup.select("script[type*=application]")[1].text)
                data = parse(location)
                yield data
            except Exception as e:
                logger.info(f"BROKEN LINK {url} : {e}")
                MISSED_CITIES.append(url)
                continue

        missed_links = get_missed_cities(MISSED_CITIES)
        logger.info(f"Total broken or missed urls: {len(missed_links)}")
        for url in missed_links:
            logger.info(f"Crawling missed link: {url}")
            driver.get_and_wait_for_request(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            location = json.loads(soup.select("script[type*=application]")[1].text)
            data = parse(location)
            yield data


def scrape():
    logger.info(f"Start Crawling {DOMAIN} ...")
    CrawlStateSingleton.get_instance().save(override=True)
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
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
