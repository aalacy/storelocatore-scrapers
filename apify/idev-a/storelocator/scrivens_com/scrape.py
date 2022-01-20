from sgscrape import simple_scraper_pipeline as sp
from sgselenium.sgselenium import SgChrome
from sgpostal.sgpostal import parse_address_intl
from sglogging import sglog
import json
from bs4 import BeautifulSoup
import tenacity
import os

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

os.environ[
    "PROXY_URL"
] = "http://groups-RESIDENTIAL,country-gb:{}@proxy.apify.com:8000/"

log = sglog.SgLogSetup().get_logger(logger_name="scrivens")

sitemap = "https://scrivens.com/branch-sitemap.xml"

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)

MISSING = "<MISSING>"
country_code = "UK"
locator_domain = "scrivens.com"


@tenacity.retry(stop=tenacity.stop_after_attempt(10), wait=tenacity.wait_fixed(5))
def get_with_retry(url):
    with SgChrome(user_agent=user_agent) as driver:
        log.info(f"Crawling: {url}")
        driver.get(url)
        htmlmaps = driver.page_source
        return htmlmaps


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
        log.info(f"No Address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetch_data():
    htmlmaps = get_with_retry(sitemap)
    soup_map = BeautifulSoup(htmlmaps, "html.parser")
    links = [link["href"] for link in soup_map.select("a[href*=branch]")]

    for link in links:
        html = get_with_retry(link)
        soup = BeautifulSoup(html, "html.parser")
        json_data = json.loads(soup.select("div#jsonMapLocations")[0].text.strip())
        for loc in json_data.values():

            if loc["is_optical"]:
                store_number = loc["ID"]
                location_name = loc["name"]
                address = loc["address"]
                address = address.replace("<br />", ",").replace("\r\n", ",")
                street_address, city, state, zip_postal = get_address(address)
                zip_postal = loc["postcode"]
                phone = loc["phone_number"]
                page_url = link
                # sgpostal failed for these UK ancient cities
                if location_name == "Driffield":
                    city = location_name
                if location_name == "Cottingham":
                    city = location_name
                if location_name == "Radcliffe":
                    city = location_name
                if location_name == "Stone":
                    city = location_name

                latitude = loc["lat"]
                longitude = loc["lng"]
                hoo = str(loc["opening_times"])
                hours = hoo.replace("{", "").replace("'", "").replace("}", "")
                location_type = "Vision branch"
            else:
                continue

        yield {
            "locator_domain": locator_domain,
            "page_url": page_url,
            "location_name": location_name,
            "latitude": latitude,
            "longitude": longitude,
            "city": city,
            "store_number": store_number,
            "street_address": street_address,
            "state": state,
            "zip": zip_postal,
            "phone": phone,
            "location_type": location_type,
            "hours": hours,
            "country_code": country_code,
        }


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"]),
        page_url=sp.MappingField(mapping=["page_url"], part_of_record_identity=True),
        location_name=sp.MappingField(
            mapping=["location_name"],
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
        ),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], is_required=False
        ),
        city=sp.MappingField(mapping=["city"], is_required=False),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MultiMappingField(mapping=["zip"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"]),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(
            mapping=["store_number"],
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"], is_required=False),
        location_type=sp.MappingField(mapping=["location_type"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )
    pipeline.run()


scrape()
