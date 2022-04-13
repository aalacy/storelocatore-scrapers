from sgselenium.sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
import ssl
import re

ssl._create_default_https_context = ssl._create_unverified_context
MISSING = "<MISSING>"
DOMAIN = "davidjones.com"
logger = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
store_locator = "https://www.davidjones.com/stores"


def parse_json(soup, driver):
    data = {}
    data["locator_domain"] = DOMAIN
    data["location_name"] = soup.select_one(
        "li.active span[itemprop=title]"
    ).text.strip()
    data["store_number"] = MISSING
    data["page_url"] = driver.current_url
    data["location_type"] = "Store"

    data["street_address"] = soup.select_one("span.store-suburb").text.strip()
    try:
        data["city"] = soup.select_one("span.store-city").text.strip()
    except Exception as e:
        logger.info(f"Missing City - trying another tag, Err: {e}")
        data["city"] = soup.select_one("span.store-suburb").text.strip()

    data["state"] = soup.select_one("span.store-state").text.strip()
    if soup.select_one("span.store-country").text.strip() == "Australia":
        data["country_code"] = "AU"
    elif soup.select_one("span.store-country").text.strip() == "New Zealand":

        data["country_code"] = "NZ"
    else:
        data["country_code"] = "<MISSING>"

    data["zip_postal"] = soup.select_one("span.store-postcode").text.strip()
    data["phone"] = soup.select_one("span.tel-no").text.strip()
    data["latitude"] = soup.select_one("meta[itemprop=latitude]")["content"]
    data["longitude"] = soup.select_one("meta[itemprop=longitude]")["content"]
    ooh = []
    for row in soup.select("tr"):
        day = (row.select("td")[0].text).replace("\r", " ").replace("\n", "").strip()
        time = (row.select("td")[1].text).replace("\r", " ").replace("\n", "").strip()
        ooh.append(day + ": " + time)

    ooh = ", ".join(ooh)
    data["hours_of_operation"] = ooh

    return data


def fetch_data():
    with SgChrome() as driver:

        driver.get(store_locator)
        soup = bs(driver.page_source, "html.parser")
        pull_str = re.search(
            r"window\.geodata = ({.*})",
            soup.select_one('script[type*=javascript]:-soup-contains("window.geodata")')
            .text.strip()
            .replace("\n", "")
            .replace("\t", ""),
        ).group(1)
        stores = [
            "https://www.davidjones.com/stores/" + store
            for store in re.findall('"/stores/([A-Za-z-0-9]*)"', pull_str)
        ]
        stores.append("https://www.davidjones.com/newmarket")
        stores.append("https://www.davidjones.com/sunshine")
        stores.append("https://www.davidjones.com/wollongong-central")
        for store in stores:
            logger.info(f"Crawling: {store}")
            driver.get(store)
            soup2 = bs(driver.page_source, "html.parser")
            i = parse_json(soup2, driver)
            yield i


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
        log_stats_interval=1,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
