from sgselenium import SgFirefox
import time
from bs4 import BeautifulSoup as bs
from sgscrape import simple_scraper_pipeline as sp
import json
from html import unescape


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
    url = "https://www.paulsmith.com/uk/stores"
    with SgFirefox(
        block_third_parties=True,
        is_headless=True,
        proxy_country="uk",
    ) as driver:
        driver.get(url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        scroll_pause = 0.5

        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(scroll_pause)

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        response = driver.page_source

        soup = bs(response, "html.parser")
        page_urls = []
        for page_url in [
            "https://www.paulsmith.com" + a_tag["href"]
            for a_tag in soup.find_all(
                "a", attrs={"class": "flex flex-col items-center"}
            )
        ]:
            if page_url not in page_urls:
                page_urls.append(page_url)

        for page_url in page_urls:
            locator_domain = "paulsmith.com"

            driver.get(page_url)
            loc_response = driver.page_source

            try:
                loc_data = extract_json(loc_response.split("ld+json")[1])[0]

                location_name = loc_data["name"]
                latitude = loc_data["geo"][0]["latitude"]
                longitude = loc_data["geo"][0]["longitude"]
                city = loc_data["address"][0]["addressLocality"]
                store_number = "<MISSING>"
                address = loc_data["address"][0]["streetAddress"]

                state = loc_data["address"][0]["addressRegion"]
                if state.lower() == "na" or state == "N/A":
                    state = "<MISSING>"

                zipp = loc_data["address"][0]["postalCode"]
                phone = loc_data["telephone"]
                location_type = loc_data["@type"]
                country_code = loc_data["address"][0]["addressCountry"]

                hours = ""
                for part in loc_data["openingHours"]:
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

            except Exception:
                loc_data = extract_json(unescape(loc_response).split('"app"')[1])[0][
                    "props"
                ]["shop"]

                location_name = loc_data["title"]
                latitude = loc_data["latitude"]
                longitude = loc_data["longitude"]
                city = loc_data["city"]
                store_number = "<MISSING>"

                try:
                    address = (
                        loc_data["address_line_1"] + " " + loc_data["address_line_2"]
                    )
                except Exception:
                    address = loc_data["address_line_1"]
                state = "<MISSING>"
                zipp = loc_data["postcode"]
                if zipp == "na":
                    zipp = "<MISSING>"

                phone = loc_data["telephone"]
                location_type = "<MISSING>"
                country_code = loc_data["country_name"]

                try:
                    hours_parts = json.loads(loc_data["opening_hours"])

                    hours = ""
                    count = 0
                    for day in hours_parts["weekday"].keys():
                        if (
                            hours_parts["weekday"][day]["not_open"] == "1"
                            or hours_parts["weekday"][day]["open"].lower() == "closed"
                        ):
                            hours = hours + day + " closed" + ", "
                            count = count + 1
                        else:
                            start = hours_parts["weekday"][day]["open"]
                            end = hours_parts["weekday"][day]["close"]

                            hours = hours + day + " " + start + "-" + end + ", "

                    hours = hours[:-2]
                    if count == 7:
                        hours = "CLOSED"

                except Exception:
                    hours = "<MISSING>"

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
