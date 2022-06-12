import re
import json
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgzip.dynamic import DynamicZipSearch, SearchableCountries, Grain_2
from sgscrape import simple_scraper_pipeline as sp


def extract_json(html_string):
    html_string = (
        html_string.replace("\n", "")
        .replace("\r", "")
        .replace("\t", "")
        .replace(" /* forcing open state for all FCs*/", "")
    )
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
    page_urls = []
    session = SgRequests()
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        granularity=Grain_2(),
        expected_search_radius_miles=10,
    )

    for search_code in search:
        search.found_nothing()
        url = (
            "https://www.regions.com/Locator?regions-get-directions-starting-coords=&daddr=&autocompleteAddLat=&autocompleteAddLng=&r=&geoLocation="
            + search_code
            + "&type=branch"
        )

        response_stuff = session.get(url)
        response = response_stuff.text
        first_objects = extract_json(response)
        soup = bs(response, "html.parser")
        grids = soup.find_all("li", attrs={"class": "locator-result__list-item"})

        x = 0
        for location in first_objects:
            other_check = "failing"
            try:
                location_name = location["title"]
            except Exception:
                continue

            locator_domain = "regions.com"

            a_tag = grids[x].find("a")
            x = x + 1
            try:
                page_url = "regions.com" + a_tag["href"]
            except Exception:
                page_url = "<MISSING>"
            latitude = location["lat"]
            longitude = location["lng"]
            address = location["address"].split("<br />")[0]
            if bool(re.search("[a-zA-Z]", address)) is False:
                address = "<MISSING>"
            city = location["address"].split("<br />")[1].split(",")[0]

            state_parts = (
                location["address"].split("<br />")[1].split(",")[1].split(" ")
            )
            state = ""
            for item in range(len(state_parts) - 1):
                state = state + state_parts[item] + " "

            state = state.strip()

            zipp = location["address"].split("<br />")[1].split(",")[1].split(" ")[-1]
            country_code = "US"
            store_number = location["itemId"]
            location_type = "atm"
            location_type_check = location["type"]

            if page_url != "<MISSING>":
                try:
                    page_url = page_url.lower()
                    if page_url in page_urls:
                        continue

                    response_stuff = session.get("https://" + page_url)
                    response = response_stuff.text

                    if (
                        "ATM Location and Features" not in response
                        and "-atm-" not in page_url
                    ):
                        continue
                    other_check = "passing"
                    json_objects = extract_json(response)

                    for item in json_objects:
                        if "name" not in item.keys():
                            continue
                        else:
                            try:
                                phone = item["telephone"].replace("+", "")
                            except Exception:
                                phone = "<MISSING>"
                                pass

                    hours_soup = bs(response, "html.parser")
                    lis = hours_soup.find_all("li")

                    for li in lis:
                        if "ATM Hours" in li.text.strip():
                            hours = li.text.strip().replace("ATM Hours: ", "")

                except Exception:
                    phone = "<MISSING>"
                    hours = "<MISSING>"

            else:
                phone = "<MISSING>"
                hours = "<MISSING>"

            page_urls.append(page_url)
            if location_type_check != "atm" and other_check != "passing":
                continue

            hours = hours.replace("<br/>", " ").strip()

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
