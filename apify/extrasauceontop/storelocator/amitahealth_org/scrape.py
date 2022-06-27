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
    url = "https://www.amitahealth.org/find-a-location/?page=1&count=5000"

    response = session.get(url).text
    json_objects = extract_json(response)
    data = extract_json(json_objects[-1]["SettingsData"])
    locations = extract_json(data[0]["EntityJsonData"])

    for location in locations:
        locator_domain = "amitahealth.org"
        page_url = "https://www.amitahealth.org/location/" + location["DirectUrl"]

        if (
            page_url
            == "https://www.amitahealth.org/location/amita-health-medical-group"
            or page_url == "https://www.amitahealth.org/location/er-wait-times"
        ):
            continue

        location_name = location["Name"]

        if location_name == "Provider Locations":
            continue

        address = (location["Address1"] + " " + location["Address2"]).strip()
        city = location["City"]
        state = location["StateName"]
        zipp = location["PostalCode"]
        country_code = "US"
        store_number = location["Id"]
        phone = location["Phone"]
        location_type = location["OrgType"]
        latitude = location["Latitude"]
        longitude = location["Longitude"]

        hours_response = session.get(page_url).text

        hours_data = extract_json(hours_response)

        settingsdata = json.loads(hours_data[4]["SettingsData"])

        hours_contenders = settingsdata["StaticPageZones"][0]["Value"]["FieldColumns"][
            2
        ]["Fields"]

        for item in hours_contenders:
            if item["PublicLabel"] == "Office Hours":
                hours_parts = item

        hours = ""
        for part in hours_parts["Values"]:
            hours = hours + part + ", "

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
