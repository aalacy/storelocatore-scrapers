from sgrequests import SgRequests
from sgscrape import simple_scraper_pipeline as sp
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_8


def get_data():
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN],
        granularity=Grain_8(),
        expected_search_radius_miles=25,
    )
    session = SgRequests()
    url = "https://www.bupa.co.uk/BDC/GoogleMapSearch"

    for search_lat, search_lon in search:
        x = 0
        while True:
            x = x + 1
            params = {
                "latitude": str(search_lat),
                "longitude": str(search_lon),
                "searchFilter": [],
                "dataCount": "1",
                "pageIndex": x,
                "campaignId": None,
            }

            response = session.post(url, json=params)
            try:
                response = response.json()
            except Exception:
                search.found_nothing()
                break
            if len(response) == 0:
                break
            for location in response:
                locator_domain = "www.bupa.co.uk"
                page_url = "https://www.bupa.co.uk" + location["PageUrl"]
                location_name = location["PageTitle"]
                latitude = location["Latitude"]
                longitude = location["Longitude"]
                search.found_location_at(latitude, longitude)
                store_number = "<MISSING>"

                address_parts = location["FullAddress"].split(", ")

                if len(address_parts) == 2:
                    city = "<MISSING>"
                    address = address_parts[0]
                    zipp = address_parts[-1]
                    state = "<MISSING>"
                    country_code = "UK"

                elif len(address_parts) > 2:
                    address = "".join(part + " " for part in address_parts[:-2])
                    city = address_parts[-2]
                    zipp = address_parts[-1]
                    state = "<MISSING>"
                    country_code = "UK"

                location_type = "<MISSING>"

                phone = "<LATER>"
                hours = "<LATER>"

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
