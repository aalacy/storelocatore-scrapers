from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_1_KM
from sgscrape import simple_scraper_pipeline as sp
from concurrent.futures import ThreadPoolExecutor, as_completed
from sglogging import sglog
import os

log = sglog.SgLogSetup().get_logger(logger_name="allpoint")
session = SgRequests()


def get_location(search_codes):
    search_lat = search_codes[0]
    search_lon = search_codes[1]
    log.info(search_lat)
    log.info(search_lon)
    url = "https://clsws.locatorsearch.net/Rest/LocatorSearchAPI.svc/GetLocations"

    x = 0
    while True:
        x = x + 1
        params = {
            "Latitude": str(search_lat),
            "Longitude": str(search_lon),
            "Miles": "100",
            "NetworkId": "10029",
            "PageIndex": str(x),
            "SearchByOptions": "",
        }

        response = session.post(url, json=params).json()
        locs = []
        try:
            for location in response["data"]["ATMInfo"]:
                locator_domain = "allpointnetwork.com"
                page_url = "https://clsws.locatorsearch.net/Rest/LocatorSearchAPI.svc/GetLocations"
                location_name = "Allpoint " + location["RetailOutlet"]
                address = location["Street"]
                city = location["City"]
                state = location["State"]
                zipp = location["ZipCode"]
                country_code = location["Country"]
                if country_code == "MX":
                    continue
                store_number = location["LocationID"]
                phone = "<MISSING>"
                location_type = location["RetailOutlet"]
                latitude = location["Latitude"]
                longitude = location["Longitude"]
                hours = "<MISSING>"
                locs.append(
                    {
                        "locator_domain": locator_domain,
                        "page_url": page_url,
                        "location_name": location_name,
                        "latitude": latitude,
                        "longitude": longitude,
                        "city": city,
                        "store_number": store_number,
                        "street_address": address,
                        "state": state,
                        "zip": zipp,
                        "phone": phone,
                        "location_type": location_type,
                        "hours": hours,
                        "country_code": country_code,
                    }
                )
            if len(response["data"]["ATMInfo"]) < 100:
                break
        except Exception:
            break

    return locs


def scrape_loc_urls():

    search = DynamicGeoSearch(
        country_codes=[
            SearchableCountries.USA,
            SearchableCountries.CANADA,
            SearchableCountries.BRITAIN,
        ],
        granularity=Grain_1_KM(),
    )

    codes = []
    for search_lat, search_lon in search:
        codes.append([search_lat, search_lon])

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(get_location, search_codes) for search_codes in codes
        ]
        for future in as_completed(futures):
            try:
                record = future.result()
                if record:
                    for rec in record:
                        yield rec
            except Exception as e:
                log.error(str(e))


def scrape():

    try:
        proxy_pass = os.environ["PROXY_PASSWORD"]

    except Exception:
        proxy_pass = "No"

    if proxy_pass != "No":
        raise Exception("Do not run this with a proxy")

    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"]),
        page_url=sp.MappingField(mapping=["page_url"], part_of_record_identity=True),
        location_name=sp.MappingField(
            mapping=["location_name"], part_of_record_identity=True
        ),
        latitude=sp.MappingField(mapping=["latitude"], part_of_record_identity=True),
        longitude=sp.MappingField(mapping=["longitude"], part_of_record_identity=True),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], is_required=False
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MultiMappingField(mapping=["zip"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"]),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(
            mapping=["store_number"], part_of_record_identity=True
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"], is_required=False),
        location_type=sp.MappingField(mapping=["location_type"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=scrape_loc_urls,
        field_definitions=field_defs,
        log_stats_interval=15,
    )
    pipeline.run()


scrape()
