from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgscrape import simple_scraper_pipeline as sp
import json

session = SgRequests(dont_retry_status_codes=[500, 404])
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("dodge_com")

search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_search_results=100,
    expected_search_radius_miles=100,
)


def get_data():
    for search_code in search:
        logger.info("Pulling Zip Code %s..." % search_code)
        url = (
            "https://www.dodge.com/bdlws/MDLSDealerLocator?brandCode=D&func=SALES&radius=500&resultsPage=1&resultsPerPage=100&zipCode="
            + search_code
        )
        try:
            r = session.get(url, headers=headers)
            dealers = r.json()["dealer"]

        except Exception:
            search.found_nothing()
            continue

        if len(dealers) == 0:
            search.found_nothing()
            continue

        for dealer in dealers:
            locator_domain = "dodge.com"
            page_url = dealer["website"]
            location_name = dealer["dealerName"]
            latitude = dealer["dealerShowroomLatitude"]
            longitude = dealer["dealerShowroomLongitude"]
            search.found_location_at(latitude, longitude)
            city = dealer["dealerCity"]
            store_number = dealer["dealerCode"]
            address = (dealer["dealerAddress1"] + dealer["dealerAddress2"]).strip()
            state = dealer["dealerState"]
            zipp = dealer["dealerZipCode"][0:5]
            location_type = "<MISSING>"
            country_code = dealer["dealerShowroomCountry"]
            phone = dealer["phoneNumber"]

            hours = ""

            for day in dealer["departments"]["sales"]["hours"].keys():
                if dealer["departments"]["sales"]["hours"][day]["closed"] is True:
                    hours = hours + day + " closed, "

                else:
                    sta = (
                        dealer["departments"]["sales"]["hours"][day]["open"]["time"]
                        + dealer["departments"]["sales"]["hours"][day]["open"]["ampm"]
                    )
                    end = (
                        dealer["departments"]["sales"]["hours"][day]["close"]["time"]
                        + dealer["departments"]["sales"]["hours"][day]["close"]["ampm"]
                    )
                    hours = hours + day + " " + sta + "-" + end + ", "

            hours = hours[:-2]
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
        page_url=sp.MappingField(mapping=["page_url"], is_required=False),
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
