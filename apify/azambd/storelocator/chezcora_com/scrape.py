import re
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl

from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog

session = SgRequests()
DOMAIN = "chezcora.com"
MISSING = "<MISSING>"
logger = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

restaurants_sitemap = "https://www.chezcora.com/restaurants-sitemap.xml"


def getAddress(raw_address):
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
        logger.info(f"No valid address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def parse_json(soup2, page_url):
    data = {}
    data["locator_domain"] = DOMAIN
    data["location_name"] = bs(
        str(soup2.find("h1", id="title")).replace("<br/>", " "), "lxml"
    ).text
    data["store_number"] = MISSING
    data["page_url"] = page_url
    data["location_type"] = "Chezcora"
    addresses = soup2.find("div", id="code_block-31-35").text
    addresses = addresses.replace("B.C.,", "").replace("S.E.", "")
    street_address, city, state, zip_postal = getAddress(addresses)
    data["street_address"] = street_address
    data["city"] = city
    data["state"] = state
    data["country_code"] = "CA"
    data["zip_postal"] = zip_postal
    data["phone"] = re.findall(r"\(\d+\) \d+-\d+", str(soup2))[0]
    data["latitude"] = re.findall(r"(\d+\.\d+,-?\d+\.\d+)", str(soup2))[0].split(",")[0]
    data["longitude"] = re.findall(r"(\d+\.\d+,-?\d+\.\d+)", str(soup2))[0].split(",")[
        1
    ]
    data["raw_address"] = f"{street_address}, {city}, {state} {zip_postal}".replace(
        MISSING, ""
    )
    data["hours_of_operation"] = ", ".join(
        [
            day["class"][0].title() + f": {day.text}"
            for day in soup2.select_one("div.opening-hours.hours").select("div")
        ]
    )

    return data


def fetch_data():

    response = session.get(restaurants_sitemap)
    soup = bs(response.text, "lxml")
    restaurants = soup.select("loc")
    # First 2 links are related to list of dinner and lunch restaurants so skipped these
    for restaurant in restaurants[2:]:
        page_url = restaurant.text
        response_detail = session.get(page_url)
        soup2 = bs(response_detail.text, "lxml")
        data = parse_json(soup2, page_url)
        yield data


def scrape():
    logger.info(f"Start Crawling {DOMAIN} ...")
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(DOMAIN),
        page_url=sp.MappingField(mapping=["page_url"], is_required=False),
        location_name=sp.MappingField(mapping=["location_name"]),
        latitude=sp.MappingField(mapping=["latitude"], part_of_record_identity=True),
        longitude=sp.MappingField(mapping=["longitude"], part_of_record_identity=True),
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
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
