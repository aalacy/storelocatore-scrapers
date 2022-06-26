from sgrequests import SgRequests
import json
from sgscrape import simple_scraper_pipeline as sp
from sgselenium import SgFirefox
import html
import time


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
    url = "https://connect.shore.com/bookings/beautyhairshop-heilbronn-stadtgalerie/locations?locale=de&origin=standalone"
    with SgRequests() as session:
        response = session.get(url).text

        json_objects = extract_json(response)
        locations = json_objects[0]["beautyhairshop-heilbronn-stadtgalerie"][
            "locations"
        ]
        for store_number in locations.keys():
            locator_domain = "cosmo-gmbh.de/beautyhairshop"
            page_url = (
                "https://connect.shore.com/bookings/"
                + locations[store_number]["id"]
                + "/services?locale=de&origin=standalone"
            )
            location_name = locations[store_number]["name"]
            city = locations[store_number]["cityName"].split(" (")[0]
            address = html.unescape(locations[store_number]["street"])
            state = "<MISSING>"
            zipp = locations[store_number]["postalCode"]
            location_type = "<MISSING>"
            country_code = "DE"

            with SgFirefox(is_headless=True) as driver:
                driver.get(page_url)
                time.sleep(30)
                driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))
                page_response = driver.page_source

            latitude = page_response.split("www.google.com/maps/@")[1].split(",")[0]
            longitude = page_response.split("www.google.com/maps/@")[1].split(",")[1]

            hours = "<MISSING>"
            phone = "<MISSING>"

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
