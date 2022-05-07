from sgrequests import SgRequests
from sgscrape import simple_scraper_pipeline as sp
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def get_data():
    search = DynamicZipSearch(country_codes=[SearchableCountries.USA])

    x = 0
    for search_code in search:
        x = x + 1
        if x == 1000:
            return
        url = (
            "https://satruck.org/apiservices/pickup/donategoods/locations?Type=3&ZipCode="
            + str(search_code)
        )
        session = SgRequests()
        response = session.get(url).json()

        for location in response["RetVal"]["Locations"]:
            locator_domain = "satruck.org"
            page_url = location["Website"]
            location_name = location["Name"]
            latitude = location["Latitude"]
            longitude = location["Longitude"]
            city = location["City"]
            store_number = location["Id"]
            address = (location["Address1"] + " " + location["Address2"]).strip()
            state = location["State"]
            zipp = location["Zip"]
            phone = location["ContactPhone"]
            location_type = "Drop Off"
            hours = (
                location["Hours"]
                .replace(" | ", " ")
                .replace(" / ", " ")
                .lower()
                .replace("store & donation hours: ", "")
                .replace("  ", " ")
                .replace("store hours: ", "")
                .split("donation hours:")[0]
            )
            if "open" in hours:
                hours = hours.split("open")[1]

            country_code = "US"
            search.found_location_at(latitude, longitude)

            if "temporarily closed" in hours.lower():
                continue

            if "call" in hours:
                hours = "<MISSING>"

            if len(hours) <= 2:
                hours = "<MISSING>"

            if page_url is None:
                page_url = "<MISSING>"
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
