from sgselenium import SgChrome
from sgscrape import simple_scraper_pipeline as sp
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def get_data():
    type_dict = {
        "1": "hospital",
        "3": "emergency room",
        "2": "clinic and outpatient center",
        "5": "urgent care",
        "6": "walk in care",
        "7": "pharmacy",
        "4": "imaging",
    }

    start_url = "https://www.novanthealth.org/"
    while True:
        try:
            with SgChrome() as driver:
                driver.get(start_url)
                data = driver.execute_async_script(
                    """
                var done = arguments[0]
                fetch('https://www.novanthealth.org/DesktopModules/NHLocationFinder/API/Location/ByType', {
                    "headers": {
                        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                        "x-requested-with": "XMLHttpRequest"
                    },
                    "body": "LocationGroupId=1&Latitude=&Longitude=&Distance=5&SubTypes=&Keyword=&SortOrder=&MaxLocations=5000&MapBounds=",
                    "method": "POST"
                })
                .then(res => res.json())
                .then(data => done(data))
                """
                )
            break
        except Exception:
            continue

    for location in data["Locations"]:
        locator_domain = "novanthealth.org"
        page_url = location["WebsiteUrl"]
        location_name = location["BusinessName"]
        address = location["AddressLine"]
        city = location["City"]
        state = location["State"]
        zipp = location["PostalCode"]
        country_code = "US"
        store_number = location["StoreCode"].replace("-", "")
        phone = location["PrimaryPhone"]
        try:
            location_type_keys = location["LocationTypeIds"]
            location_type = "<MISSING>"
            for item in location_type_keys:
                if str(item) in type_dict.keys():
                    location_type = type_dict[str(item)]
                    break
        except Exception:
            location_type = "<MISSING>"
        latitude = location["Latitude"]
        longitude = location["Longitude"]
        hours = ""
        if "Open 24 hours" in location["HoursInfo"]["Display"].keys():
            hours = "Open 24 hours"
        else:
            days = location["HoursInfo"]["Display"].keys()
            for day in days:
                time = location["HoursInfo"]["Display"][day]
                hours = hours + day + " " + time + ", "
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
        log_stats_interval=15,
    )
    pipeline.run()


scrape()
