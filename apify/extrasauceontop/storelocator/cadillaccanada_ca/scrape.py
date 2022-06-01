from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicZipSearch, SearchableCountries, Grain_1_KM
from sgscrape import simple_scraper_pipeline as sp

logger = SgLogSetup().get_logger("cadillaccanada_ca")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/json",
    "host": "www.cadillacoffers.ca",
    "x-requested-with": "XMLHttpRequest",
}

search = DynamicZipSearch(
    country_codes=[SearchableCountries.CANADA],
    granularity=Grain_1_KM(),
    expected_search_radius_miles=5,
)


def get_data():
    x = 0
    for zipcode in search:
        x = x + 1
        url = (
            "https://www.cadillacoffers.ca/apps/leap/readDealersJson?searchType=postalCodeSearch&postalCode="
            + zipcode
            + "&language=en&pagePath=%2Fcontent%2Fcadillac-offers%2Fca%2Fen%2Fdealer-locations&_=1653070881080"
        )
        logger.info("Pulling Code %s..." % zipcode)

        response = session.get(url, headers=headers).json()
        for location in response["dealers"]:
            locator_domain = "cadillaccanada.ca"
            page_url = location["websiteURL"]
            location_name = location["dealerName"]
            latitude = location["latitude"]
            longitude = location["longitude"]
            city = location["city"]
            store_number = location["dealerCode"]
            address = location["streetAddress1"]
            state = location["state"]
            zipp = location["postalCode"]
            phone = location["primaryPhone"]
            location_type = "<MISSING>"
            hours = "<LATER>"
            country_code = "CA"

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


def scrape():
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
        data_fetcher=get_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )
    pipeline.run()


scrape()
