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
            phone = location["salesPhone"]
            location_type = "<MISSING>"
            country_code = "CA"

            try:
                sunday_hours = (
                    "Sunday "
                    + location["salesSundayOpen"][0:2]
                    + ":"
                    + location["salesSundayOpen"][2:4]
                    + "-"
                    + location["salesSundayClose"][0:2]
                    + ":"
                    + location["salesSundayClose"][2:4]
                )
            except Exception:
                sunday_hours = "Sunday closed"

            try:
                monday_hours = (
                    "Monday "
                    + location["salesMondayOpen"][0:2]
                    + ":"
                    + location["salesMondayOpen"][2:4]
                    + "-"
                    + location["salesMondayClose"][0:2]
                    + ":"
                    + location["salesMondayClose"][2:4]
                )
            except Exception:
                monday_hours = "Monday closed"

            try:
                tuesday_hours = (
                    "Tuesday "
                    + location["salesTuesdayOpen"][0:2]
                    + ":"
                    + location["salesTuesdayOpen"][2:4]
                    + "-"
                    + location["salesTuesdayClose"][0:2]
                    + ":"
                    + location["salesTuesdayClose"][2:4]
                )
            except Exception:
                tuesday_hours = "Tuesday closed"

            try:
                wednesday_hours = (
                    "Wednesday "
                    + location["salesWednesdayOpen"][0:2]
                    + ":"
                    + location["salesWednesdayOpen"][2:4]
                    + "-"
                    + location["salesWednesdayClose"][0:2]
                    + ":"
                    + location["salesWednesdayClose"][2:4]
                )
            except Exception:
                wednesday_hours = "Wednesday closed"

            try:
                thursday_hours = (
                    "Thursday "
                    + location["salesThursdayOpen"][0:2]
                    + ":"
                    + location["salesThursdayOpen"][2:4]
                    + "-"
                    + location["salesThursdayClose"][0:2]
                    + ":"
                    + location["salesThursdayClose"][2:4]
                )
            except Exception:
                thursday_hours = "Thursday closed"

            try:
                friday_hours = (
                    "Friday "
                    + location["salesFridayOpen"][0:2]
                    + ":"
                    + location["salesFridayOpen"][2:4]
                    + "-"
                    + location["salesFridayClose"][0:2]
                    + ":"
                    + location["salesFridayClose"][2:4]
                )
            except Exception:
                friday_hours = "Friday closed"

            try:
                saturday_hours = (
                    "Saturday "
                    + location["salesSaturdayOpen"][0:2]
                    + ":"
                    + location["salesSaturdayOpen"][2:4]
                    + "-"
                    + location["salesSaturdayClose"][0:2]
                    + ":"
                    + location["salesSaturdayClose"][2:4]
                )
            except Exception:
                saturday_hours = "Saturday closed"

            hours = (
                sunday_hours
                + ", "
                + monday_hours
                + ", "
                + tuesday_hours
                + ", "
                + wednesday_hours
                + ", "
                + thursday_hours
                + ", "
                + friday_hours
                + ", "
                + saturday_hours
            )

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
