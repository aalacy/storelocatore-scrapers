from sgrequests import SgRequests
import json
from sgscrape import simple_scraper_pipeline as sp
import re


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
    url = "https://www.bricomarche.pt/apoio-ao-cliente/horarios-de-loja/"
    response = session.get(url).text.encode("utf-16", "surrogatepass").decode("utf-16")
    json_objects = extract_json(response.split("lojas = ")[1])

    with open("file.txt", "w", encoding="utf-8") as output:
        json.dump(json_objects, output, indent=4)

    for location in json_objects:
        if "id" not in location.keys():
            continue

        locator_domain = "bricoarche.pt"
        page_url = "https://www.bricomarche.pt/lojas/" + location["slug"]
        location_name = location["name"]
        latitude = location["lat"]
        longitude = location["lng"]
        city = location["locality"]
        store_number = location["id"]

        address_parts = location["address"]
        address_parts = (
            re.sub("<[^>]+>", "", address_parts)
            .replace("\r\n", ", ")
            .replace(", , ", ", ")
            .replace(" , ", ", ")
            .replace(",,", ",")
        )

        address = address_parts.split(", ")[0]
        state = "<MISSING>"

        try:
            zipp = address_parts.split(", ")[-1].split(" ")[0]
            if any(str.isdigit(c) for c in zipp):
                pass

            else:
                zipp = "<MISSING>"

        except Exception:
            zipp = "<MISSING>"

        phone = location["phone_number"]
        location_type = "<MISSING>"
        hours = location["schedule"]
        country_code = "Portugal"

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
