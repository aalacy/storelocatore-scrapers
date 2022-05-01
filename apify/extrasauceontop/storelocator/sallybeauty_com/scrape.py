from sgselenium.sgselenium import SgChrome
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_8
import json
from sgscrape import simple_scraper_pipeline as sp
from bs4 import BeautifulSoup as bs
import html
from webdriver_manager.chrome import ChromeDriverManager


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


def get_driver():
    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    driver = SgChrome(
        user_agent=user_agent,
        is_headless=True,
        executable_path=ChromeDriverManager().install(),
    ).driver()

    return driver


def get_data():
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        granularity=Grain_8(),
        expected_search_radius_miles=200,
    )

    for search_lat, search_lon in search:
        url = (
            "https://www.sallybeauty.com/on/demandware.store/Sites-SA-Site/default/Stores-FindStores?showMap=true&radius=250&lat="
            + str(search_lat)
            + "&long="
            + str(search_lon)
        )
        driver = None
        x = 0
        count = 300
        while True:
            x = x + 1
            if x % 2 == 0:
                count = count - 50
            url = (
                "https://www.sallybeauty.com/on/demandware.store/Sites-SA-Site/default/Stores-FindStores?showMap=true&radius="
                + str(count)
                + "&lat="
                + str(search_lat)
                + "&long="
                + str(search_lon)
            )
            if x == 10:
                raise Exception
            try:
                try:
                    driver.get(url)  # noqa
                    response = driver.page_source  # noqa
                    json_objects = extract_json(response)
                    json_objects[0]["stores"]

                except Exception:
                    if driver is not None:
                        driver.quit()
                    driver = get_driver()
                    driver.get(url)
                    response = driver.page_source
                    json_objects = extract_json(response)
                    json_objects[0]["stores"]

                break

            except Exception:
                continue

        for location in json_objects[0]["stores"]:
            locator_domain = "www.sallybeauty.com"
            page_url = url
            location_name = location["name"]
            latitude = location["latitude"]
            longitude = location["longitude"]
            city = location["city"]
            store_number = location_name.split("#")[1]
            address = location["address1"]
            if location["address2"] is not None:
                address = address + " " + location["address2"]
            state = location["stateCode"]
            zipp = location["postalCode"]
            phone = location["phone"]
            location_type = "<MISSING>"
            country_code = location["countryCode"]
            try:
                hours_soup = bs(html.unescape(location["storeHours"]), "html.parser")
                hours_parts = hours_soup.find_all(
                    "div", attrs={"class": "store-hours-day"}
                )

                hours = ""
                for part in hours_parts:
                    text_stuff = (
                        part.text.strip()
                        .replace("\r", "")
                        .replace("\n", "")
                        .replace("\t", "")
                    )
                    while "  " in text_stuff:
                        text_stuff = text_stuff.replace("  ", " ")

                    hours = hours + text_stuff + ", "
                hours = hours[:-2]

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

    driver.quit()


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(mapping=["locator_domain"]),
        page_url=sp.MappingField(mapping=["page_url"]),
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
        duplicate_streak_failure_factor=100,
    )
    pipeline.run()


scrape()
