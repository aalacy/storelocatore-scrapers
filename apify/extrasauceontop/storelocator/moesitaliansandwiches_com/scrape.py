from sgselenium import SgChrome
import json
import ssl
from sgscrape import simple_scraper_pipeline as sp

ssl._create_default_https_context = ssl._create_unverified_context


def extract_json(html_string):
    json_objects = []
    count = 0

    brace_count = 0
    for element in html_string:

        if element == "{":
            brace_count = brace_count + 1
            if brace_count == 1:
                start = count

        elif element == "}":
            brace_count = brace_count - 1
            if brace_count == 0:
                end = count
                try:
                    json_objects.append(json.loads(html_string[start : end + 1]))
                except Exception:
                    pass
        count = count + 1

    return json_objects


def get_data():
    url = "https://www.moesitaliansandwiches.com/newburyport"
    with SgChrome(block_third_parties=False) as driver:
        driver.get(url)
        response = (
            driver.page_source.replace('" + "', " + ")
            .replace('\\"', "'")
            .replace("\\n", " ")
        )

    json_objects = extract_json(response.split("window.POPMENU_APOLLO_STATE = ")[1])

    for location in json_objects[0][
        "restaurantWithLocationsQuery:{'ssr':true,'variables':{'restaurantId':3689}}"
    ]["restaurant"]["locations"]:
        locator_domain = "www.moesitaliansandwiches.com"
        page_url = "https://www.moesitaliansandwiches.com/" + location["slug"]
        location_name = location["name"]
        latitude = location["lat"]
        longitude = location["lng"]
        city = location["city"]
        store_number = location["id"]
        address = location["streetAddress"]
        state = location["state"]
        zipp = location["postalCode"]
        phone = location["phone"]
        location_type = "<MISSING>"
        country_code = "US"

        hours = ""
        for part in location["schemaHours"]:
            hours = hours + part + ", "

        hours = hours[:-2]

        if "Su" not in hours:
            hours = "Su Closed, " + hours

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


if __name__ == "__main__":
    scrape()
