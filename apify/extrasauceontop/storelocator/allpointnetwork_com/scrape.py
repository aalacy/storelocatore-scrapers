from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_2
from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
import os

log = sglog.SgLogSetup().get_logger(logger_name="allpoint")
session = SgRequests()


def get_data():
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA],
        granularity=Grain_2(),
    )

    ids = []
    for search_lat, search_lon in search:
        log.info(search_lat)
        log.info(search_lon)
        log.info("")
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
                    if store_number in ids:
                        continue

                    ids.append(store_number)
                    yield {
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

                if len(response["data"]["ATMInfo"]) < 100:
                    break
            except Exception:
                break


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
        latitude=sp.MappingField(mapping=["latitude"]),
        longitude=sp.MappingField(mapping=["longitude"]),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], part_of_record_identity=True
        ),
        city=sp.MappingField(mapping=["city"], part_of_record_identity=True),
        state=sp.MappingField(mapping=["state"], part_of_record_identity=True),
        zipcode=sp.MultiMappingField(mapping=["zip"], part_of_record_identity=True),
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
        data_fetcher=get_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )
    pipeline.run()


scrape()
