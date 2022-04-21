from sgselenium.sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl
from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

MISSING = "<MISSING>"
DOMAIN = "tisol.ca"
logger = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
store_locator = "https://www.tisol.ca/locations/"


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

            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            return street_address, city, state, zip_postal
    except Exception as e:
        logger.info(f"No Address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def parse_json(soup, page_url):
    data = {}
    data["locator_domain"] = DOMAIN
    data["store_number"] = soup.select_one("article")["id"].split("-")[1]
    data["page_url"] = page_url
    data["location_name"] = soup.select_one("h1.entry-title").text
    data["location_type"] = "Store"
    address = soup.select("h4.et_pb_module_header")[1].text
    street_address, city, state, zip_postal = get_address(address)
    data["street_address"] = street_address
    data["city"] = city
    data["state"] = state
    data["country_code"] = "CA"
    data["zip_postal"] = zip_postal
    data["phone"] = soup.select_one("h4.et_pb_module_header").text
    data["latitude"] = soup.select("div.et_pb_map_pin")[0]["data-lat"]
    data["longitude"] = soup.select("div.et_pb_map_pin")[0]["data-lng"]
    hoo = []
    for row in soup.select_one("tbody").select("tr"):
        hoo.append(row.select("td")[0].text.title() + ": " + row.select("td")[1].text)
    hoo = ", ".join(hoo)
    data["hours_of_operation"] = hoo
    data["raw_address"] = address

    return data


def fetch_data():
    with SgChrome() as driver:

        driver.get(store_locator)
        soup = bs(driver.page_source, "html.parser")
        locations = (
            soup.select("a[href*=locations]")[1:10]
            + soup.select("a[href*=locations]")[12:]
        )
        locations = [
            location["href"]
            if location["href"].startswith("https://")
            else "https://www.tisol.ca" + location["href"]
            for location in locations
        ]
        locations = list(dict.fromkeys(locations))
        for location in locations:
            page_url = location
            logger.info(f"Crawling {page_url}")
            driver.get(page_url)
            soup2 = bs(driver.page_source, "html.parser")
            i = parse_json(soup2, page_url)
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
        raw_address=sp.MappingField(mapping=["raw_address"], is_required=False),
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
