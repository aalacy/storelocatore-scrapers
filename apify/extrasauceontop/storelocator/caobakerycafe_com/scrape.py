from sgrequests import SgRequests
import cloudscraper
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
    scraper = cloudscraper.create_scraper(sess=session)

    x = 0
    while True:
        x = x + 1
        if x == 100:
            raise Exception
        try:
            url = "https://www.caobakerycafe.com/locations"
            response = scraper.get(url).text

            json_objects = extract_json(
                response.split('POPMENU_APOLLO_STATE')[1]
            )[0]
            break
        except Exception:
            session = SgRequests()
            scraper = cloudscraper.create_scraper(sess=session)
            continue

    for key in json_objects.keys():
        if "RestaurantLocation:" in key:
            location = json_objects[key]

            locator_domain = "caobakerycafe.com"
            page_url = "https://www.caobakerycafe.com/locations"
            location_name = location["name"]
            latitude = location["lat"]
            longitude = location["lng"]
            city = location["city"]
            state = location["state"]
            zipp = location["postalCode"]
            address = location["streetAddress"]
            store_number = location["id"]
            phone = location["phone"]
            location_type = "<MISSING>"
            country_code = location["country"]
            
            hours = ""
            for part in location["schemaHours"]:
                hours = hours + part + ", "
            
            hours = hours[:-2]
            if hours == "Su, Mo, Tu, We, Th, Fr, Sa":
                hours = "24/7"

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
        latitude=sp.MappingField(mapping=["latitude"]),
        longitude=sp.MappingField(mapping=["longitude"]),
        street_address=sp.MultiMappingField(
            mapping=["street_address"], part_of_record_identity=True
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
