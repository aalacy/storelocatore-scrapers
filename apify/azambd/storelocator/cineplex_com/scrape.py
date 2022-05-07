from sgrequests import SgRequests
from sgscrape import simple_scraper_pipeline as sp
from sgpostal.sgpostal import parse_address_intl
from sglogging import sglog
import json

session = SgRequests()

DOMAIN = "cineplex.com"
logger = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
MISSING = "<MISSING>"
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def get_cities():
    cities = [
        "Calgary",
        "Rocky View",
        "Red Deer County",
        "Lethbridge",
        "Edmonton",
        "Medicine Hat",
        "Sherwood Park",
        "Vernon",
        "Kelowna",
        "Kamloops",
        "Saskatoon",
        "Grande Prairie",
        "Chilliwack",
        "Moose Jaw",
        "Prince Albert",
        "Mission",
        "Abbotsford",
        "Pitt Meadows",
        "Langley",
        "Coquitlam",
        "Regina",
        "Surrey",
        "Burnaby",
        "Prince George",
        "Vancouver",
        "West Vancouver",
        "Richmond",
        "Victoria",
        "Langford",
        "Nanaimo",
        "Prince Rupert",
        "Winnipeg",
        "Thunder Bay",
        "Sault Ste. Mari",
        "Sudbury",
        "Windsor",
        "Sarnia",
        "Owen Sound",
        "North Bay",
        "Chatham",
        "Collingwood",
        "London",
        "Midland",
        "St. Thomas",
        "Waterloo",
        "Orangeville",
        "Barrie",
        "Kitchener",
        "Guelph",
        "Orillia",
        "Cambridge",
        "Brantford",
        "Brampton",
        "East Gwillimbury",
        "Milton",
        "Aurora",
        "Mississauga",
        "Vaughan",
        "Ancaster",
        "Burlington",
        "Richmond Hill",
        "Oakville",
        "Toronto",
        "Etobicoke",
        "Markham",
        "Stoney Creek",
        "Scarborough",
        "Pickering",
        "Ajax",
        "Oshawa",
        "Clarington",
        "Peterborough",
        "Welland",
        "Niagara Falls",
        "Belleville",
        "Hull",
        "Ottawa",
        "Kingston",
        "Barrhaven",
        "Brockville",
        "Cornwall",
        "Dorion",
        "Kirkland",
        "Laval",
        "Montréal",
        "Lasalle",
        "Brossard",
        "St-Bruno",
        "St. Jean",
        "Victoriaville",
        "St. Foy",
        "Québec",
        "Beauport",
        "Rock Forest",
        "Fredericton",
        "Miramichi",
        "Saint John",
        "Moncton",
        "Dieppe",
        "Yarmouth",
        "Amherst",
        "Summerside",
        "New Minas",
        "West Royalty",
        "Bridgewater",
        "Truro",
        "Lower Sackville",
        "Halifax",
        "Dartmouth",
        "New Glasgow",
        "Antigonish",
        "Sydney",
        "Corner Brook",
        "St. John'S",
    ]

    return cities


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
        logger.info(f"Address issue: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def parse_json(store):
    data = {}
    data["locator_domain"] = DOMAIN
    data["store_number"] = store["id"]
    data["page_url"] = "https://www.cineplex.com/Theatre/" + store["TheatreDetailsUrl"]
    data["location_name"] = store["title"]
    data["location_type"] = MISSING
    raw_address = store["TheatreAddress"]
    street_address, city, state, zip_postal = get_address(raw_address)
    data["street_address"] = street_address
    data["city"] = city
    data["state"] = state
    data["country_code"] = "CA"
    data["zip_postal"] = zip_postal
    data["phone"] = store["TheatrePhone"]
    data["latitude"] = MISSING
    data["longitude"] = MISSING
    data["hours_of_operation"] = MISSING
    data["raw_address"] = raw_address

    return data


def fetch_stores(city_name, page=1, stores=[]):
    api_url = f"https://search.cineplex.com/api/Search/Search?query={city_name}&from=theatredetails&siteFilter=www.cineplex.com&page={page}&lang=en-us"
    response = session.get(api_url, headers=headers)
    logger.info(f"{city_name} Response: {response}")
    data = json.loads(response.text)["TheatreDetails"]
    new_stores = data["Records"]
    pages = len(data["pages"])
    for store in new_stores:
        stores.append(store["allMeta"])

    if pages > page:
        return fetch_stores(city_name, page + 1, stores)

    return stores


def fetch_data():
    cities = get_cities()
    logger.info(f"Total Cities To Crawl: {len(cities)}")
    for city_name in cities:
        stores = fetch_stores(city_name, 1, [])
        for store in stores:
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
        log_stats_interval=1,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
