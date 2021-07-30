from sgrequests import SgRequests
import json
import html
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
    url = "https://maps.stores.claires.com/api/getAsyncLocations?template=search&level=search&search=98101&limit=10000&radius=1000000000"

    response = session.get(url).json()

    map_json = extract_json(response["maplist"])

    for location in map_json:
        locator_domain = "claires.com"
        page_url = html.unescape(location["url"])
        location_name = html.unescape(location["location_name"])
        address = location["address_1"] + " " + location["address_2"]
        address = html.unescape(address.strip())
        city = html.unescape(location["city"])
        state = html.unescape(location["region"])
        zipp = html.unescape(location["post_code"])

        country_code = html.unescape(location["country"])

        store_number = html.unescape(location["lid"])
        phone = html.unescape(location["local_phone"])
        location_type = html.unescape(location["location_type"])
        latitude = html.unescape(location["lat"])
        longitude = html.unescape(location["lng"])

        if location["location_closure_message"] == "":
            try:
                hours_section = extract_json(location["hours_sets:primary"])[0]["days"]
                days = hours_section.keys()

                hours = ""
                for day in days:
                    try:
                        start_time = hours_section[day][0]["open"]
                        end_time = hours_section[day][0]["close"]

                        hours = hours + day + " " + start_time + "-" + end_time + ", "

                    except Exception:
                        hours = hours + day + " " + hours_section[day] + ", "

                hours = html.unescape(hours[:-2])
            except Exception:
                hours = "closed"
        else:
            hours = html.unescape(location["location_closure_message"])

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
