from sgrequests import SgRequests
import json
from sgscrape import simple_scraper_pipeline as sp


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
    session = SgRequests()
    response = session.get("http://www.texaschicken.co.id/location").text.split(
        "locations = "
    )[1]

    json_objects = extract_json(response)

    for location in json_objects:
        locator_domain = "texaschicken.co.id"
        page_url = "http://www.texaschicken.co.id/location"
        location_name = location["name"]
        latitude = location["latitude"].split(",")[0]
        longitude = location["longitude"].split(",")[0]
        city = location["city"]
        store_number = location["placeid"]

        address_parts = location["content"].split(", ")

        if address_parts[-1].lower() == city.lower():
            address = ("".join(part + ", " for part in address_parts[:-1]))[:-2]

        else:
            address = ("".join(part + ", " for part in address_parts))[:-2]

        country_code = "Indonesia"

        phone = "<MISSING>"
        hours = "<MISSING>"
        location_type = "<MISSING>"
        zipp = "<MISSING>"
        state = "<MISSING>"

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
        page_url=sp.MappingField(mapping=["page_url"]),
        location_name=sp.MappingField(
            mapping=["location_name"],
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
        store_number=sp.MappingField(mapping=["store_number"], is_required=False),
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
