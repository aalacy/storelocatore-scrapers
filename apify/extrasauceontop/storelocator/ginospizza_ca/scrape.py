from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
import unidecode


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


def extract_lists(html_string):
    json_objects = []
    count = 0

    brace_count = 0
    for element in html_string:

        if element == "[":
            brace_count = brace_count + 1
            if brace_count == 1:
                start = count

        elif element == "]":
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
    url = "https://www.ginospizza.ca/locations/"
    with SgRequests() as session:
        response = session.get(url).text
        json_objects = extract_json(
            response.split("window.markers = ")[1].replace('\\"', '"')
        )
        div_objects = extract_lists(response.split("WindowContent = ")[1])[0]

        for x in range(len(div_objects)):
            location_json = json_objects[x]
            location_soup = bs(div_objects[x].replace("<br />", "\n"), "html.parser")

            locator_domain = "ginospizza.ca"
            page_url = (
                "https://www.ginospizza.ca/locations/ajax/"
                + location_json["storeNumber"]
            )
            location_name = unidecode.unidecode(location_soup.find("h3").text.strip())
            latitude = location_json["lat"].split("\\")[0]
            longitude = location_json["long"]

            address_parts = location_soup.find(
                "p", attrs={"class": "map__content"}
            ).text.strip()

            city = address_parts.split("\n")[1].split(", ")[0]
            state = address_parts.split("\n")[1].split(", ")[1]
            zipp = address_parts.split("\n")[-1]
            address = address_parts.split("\n")[0]

            store_number = location_json["storeNumber"]
            location_type = "<MISSING>"
            country_code = "CA"

            page_response = session.get(page_url).text
            page_soup = bs(page_response, "html.parser")

            phone = (
                page_soup.find("div", attrs={"class": "flexrow__gutter"})
                .text.strip()
                .split("Phone:")[1]
                .strip()
            )

            days = page_soup.find_all("dt", attrs={"class": "list--description__term"})
            times = page_soup.find_all("dd", attrs={"class": "list--description__data"})

            hours = ""
            for x in range(len(days)):
                day = days[x].text.strip()
                time = times[x].text.strip()

                hours = hours + day + " " + time + " , "
            hours = unidecode.unidecode(hours[:-2]).replace("--", "-")

            if len(hours) < 5:
                hours = "Coming Soon"

            if "310-GINO" in phone:
                phone = "310-4466"

            else:
                phone = phone.lower().split(" view")[0].replace("gine (4466)", "4466")

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
