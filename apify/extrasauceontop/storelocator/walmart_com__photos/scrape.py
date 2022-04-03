from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries, Grain_4
from sgscrape import simple_scraper_pipeline as sp


def get_data():
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], granularity=Grain_4()
    )
    session = SgRequests()
    for search_code in search:
        url = (
            "https://photos3.walmart.com/store-finder/nearest-stores.json?address="
            + str(search_code)
            + "&limit=20"
        )

        try:
            response = session.get(url).json()

        except Exception:
            continue

        for location in response["locations"]:
            locator_domain = "photos3.walmart.com"
            page_url = location["detailsPageURL"]
            location_name = location["displayName"]
            address = location["address"]["street"]
            city = location["address"]["city"]
            state = location["address"]["state"]
            zipp = location["address"]["zipcode"]
            country_code = location["address"]["country"]
            store_number = location["id"]

            try:
                phone = location["servicesMap"]["PHOTO_CENTER"]["phone"]
            except Exception:
                phone = "<MISSING>"

            location_type = location["storeType"]
            latitude = location["coordinates"]["latitude"]
            longitude = location["coordinates"]["longitude"]
            search.found_location_at(latitude, longitude)
            hours = ""
            for day in location["servicesMap"]["PHOTO_CENTER"][
                "operationalHours"
            ].keys():
                try:
                    open_time = location["servicesMap"]["PHOTO_CENTER"][
                        "operationalHours"
                    ][day]["startHr"]
                    close = location["servicesMap"]["PHOTO_CENTER"]["operationalHours"][
                        day
                    ]["endHr"]
                    hours = (
                        hours
                        + day.replace("Hrs", "")
                        + " "
                        + open_time
                        + "-"
                        + close
                        + ", "
                    )

                except Exception:
                    hours = hours + day.replace("Hrs", "") + " " + "closed" + ", "

            hours = hours[:-2]

            hours = hours.replace("monToFri", "mon to fri")
            if store_number == str("5803"):
                hours = "Open 24/7"

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
        log_stats_interval=10000,
    )
    pipeline.run()


scrape()
