from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
import json


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
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }

    base_url = "https://www.potatocornerusa.com"
    response = session.get(base_url, headers=headers).text

    soup = bs(response, "html.parser")
    state_urls = []
    state_location_urls = (
        soup.find("li", attrs={"id": "DrpDwnMn03"}).find("ul").find_all("li")
    )
    for li in state_location_urls:
        state_urls.append(li.find("a")["href"])

    state_urls = state_urls[1:]

    response = response.split("routes")[1]

    json_objects = extract_json(response)
    data = json_objects[0]

    data["./galleria-at-sunset"] = {"type": "Static", "pageId": "oki4j"}

    for key in data:
        route = key[1:]
        location_url = base_url + route
        location_data = session.get(location_url).text

        if "Store Address" in location_data and route != "/store-template":
            soup = bs(location_data, "html.parser")
            locator_domain = "potatocornerusa.com"
            page_url = location_url
            country_code = "US"
            store_number = "<MISSING>"
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours = "<MISSING>"

            location_name = soup.find("span", attrs={"class": "color_28"}).text.strip()

            coming_soon = "no"
            for url in state_urls:
                state_response = session.get(url).text
                state_soup = bs(state_response, "html.parser")
                grids = state_soup.find_all("div", attrs={"class": "_2bafp"})
                for grid in grids:
                    if "coming soon" in str(grid.text.strip().encode("utf-8").lower()):
                        grid_text = str(grid.text.strip().encode("utf-8").lower())

                        if location_name.lower() in grid_text:
                            coming_soon = "yes"

            if coming_soon == "yes":
                continue

            full_address_and_phone = soup.find_all(
                attrs={"style": "font-family:montserrat,sans-serif;"}
            )

            phone = "<MISSING>"
            for item in full_address_and_phone:
                if item.text.strip() == "Store Address:":
                    full_address = (
                        full_address_and_phone[full_address_and_phone.index(item) + 1]
                        .text.strip()
                        .replace("\n", ",")
                        .replace("Adress: ", "")
                        .split(" ")
                    )
                    zipp = full_address[-1]
                    if len(zipp) > 5:
                        zipp = zipp[1:]

                    try:
                        int(zipp[-1])
                        state = full_address[-2].replace(",", "")
                        city = full_address[-3].replace(",", "")
                        city_parts = full_address[:-3]
                        street = ""
                        for part in city_parts:
                            street = street + part.replace(",", "") + " "

                    except Exception:
                        zipp = "<MISSING>"
                        state = full_address[-1].replace(",", "")
                        city = full_address[-2].replace(",", "")
                        city_parts = full_address[:-2]
                        street = ""
                        for part in city_parts:
                            street = street + part.replace(",", "") + " "

                if item.text.strip() == "Phone Number:":
                    phone = (
                        full_address_and_phone[full_address_and_phone.index(item) + 1]
                        .text.strip()
                        .replace("(", "")
                        .replace(") ", "-")
                    )
                    if "N/A" in phone:
                        phone = "<MISSING>"

            yield {
                "locator_domain": locator_domain,
                "page_url": page_url,
                "location_name": location_name,
                "latitude": latitude,
                "longitude": longitude,
                "city": city,
                "store_number": store_number,
                "street_address": street,
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
