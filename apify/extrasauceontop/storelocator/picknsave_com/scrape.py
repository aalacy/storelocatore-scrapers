from sgrequests import SgRequests
from sgscrape import simple_scraper_pipeline as sp
from sgzip.dynamic import DynamicZipSearch, SearchableCountries, Grain_2


def get_data():
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], granularity=Grain_2()
    )
    session = SgRequests(retry_behavior=False)
    headers = {
        "User-Agent": "PostmanRuntime/7.19.0",
        "Upgrade-Insecure-Requests": "1",
        "DNT": "1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
    }

    for search_code in search:
        if len(str(search_code)) == 4:
            my_code = "0" + str(search_code)
        else:
            my_code = search_code

        url = (
            "https://www.picknsave.com/atlas/v1/stores/v1/search?filter.query="
            + my_code
        )

        x = 0
        while True:
            x = x + 1
            try:
                response = session.get(url, headers=headers, timeout=5 + x).json()
                break
            except Exception:
                continue

        for location in response["data"]["storeSearch"]["fuelResults"]:
            locator_domain = "picknsave.com"
            page_url = (
                "https://www.picknsave.com/stores/grocery/"
                + location["address"]["address"]["stateProvince"].lower()
                + "/"
                + location["address"]["address"]["cityTown"].lower().replace(" ", "-")
                + "/"
                + location["banner"]
                + "/"
                + location["divisionNumber"]
                + "/"
                + location["storeNumber"]
            )
            location_name = location["vanityName"]
            if location_name[0:3] == "PNS":
                location_name = "Pick n Save" + location_name[3:]
            latitude = location["location"]["lat"]
            longitude = location["location"]["lng"]
            search.found_location_at(latitude, longitude)
            city = location["address"]["address"]["cityTown"]
            store_number = location["locationId"]

            address = ""
            for part in location["address"]["address"]["addressLines"]:
                address = address + part + " "

            address = address.strip()
            state = location["address"]["address"]["stateProvince"]
            zipp = location["address"]["address"]["postalCode"]

            try:
                phone = location["phoneNumber"]

            except Exception:
                phone = "<MISSING>"

            location_type = location["brand"]

            if location["open24Hours"] is True:
                hours = "24/7"

            else:
                try:
                    hours = ""
                    for part in location["formattedHours"]:
                        day = part["displayName"]
                        time = part["displayHours"]
                        hours = hours + day + " " + time + ", "

                    hours = hours[:-2]
                except Exception:
                    hours = "<MISSING>"

            country_code = location["address"]["address"]["countryCode"]

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

        for location in response["data"]["storeSearch"]["results"]:
            locator_domain = "picknsave.com"
            page_url = (
                "https://www.picknsave.com/stores/grocery/"
                + location["address"]["address"]["stateProvince"].lower()
                + "/"
                + location["address"]["address"]["cityTown"].lower().replace(" ", "-")
                + "/"
                + location["banner"]
                + "/"
                + location["divisionNumber"]
                + "/"
                + location["storeNumber"]
            )
            location_name = location["vanityName"]
            if location_name[0:3] == "PNS":
                location_name = "Pick n Save" + location_name[3:]
            latitude = location["location"]["lat"]
            longitude = location["location"]["lng"]
            search.found_location_at(latitude, longitude)
            city = location["address"]["address"]["cityTown"]
            store_number = location["locationId"]

            address = ""
            for part in location["address"]["address"]["addressLines"]:
                address = address + part + " "

            address = address.strip()
            state = location["address"]["address"]["stateProvince"]
            zipp = location["address"]["address"]["postalCode"]

            try:
                phone = location["phoneNumber"]

            except Exception:
                phone = "<MISSING>"

            location_type = location["brand"]

            if location["open24Hours"] is True:
                hours = "24/7"

            else:
                try:
                    hours = ""
                    for part in location["formattedHours"]:
                        day = part["displayName"]
                        time = part["displayHours"]
                        hours = hours + day + " " + time + ", "

                    hours = hours[:-2]
                except Exception:
                    hours = "<MISSING>"

            country_code = location["address"]["address"]["countryCode"]

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
        location_type=sp.MappingField(
            mapping=["location_type"], part_of_record_identity=True
        ),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=get_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )
    pipeline.run()


scrape()
