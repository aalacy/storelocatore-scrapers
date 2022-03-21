from sgrequests import SgRequests
import json
from sgscrape import simple_scraper_pipeline as sp
from sgzip.dynamic import DynamicZipSearch, SearchableCountries, Grain_1_KM
from bs4 import BeautifulSoup as bs


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

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        granularity=Grain_1_KM(),
    )

    page_urls = []
    headers = {
        "User-Agent": "PostmanRuntime/7.19.0",
        "Upgrade-Insecure-Requests": "1",
        "DNT": "1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
    }

    session = SgRequests(retry_behavior=None)
    for zipcode in search:
        if len(str(zipcode)) == 4:
            search_code = "0" + zipcode

        else:
            search_code = zipcode

        search_url = (
            "https://maps.mattressfirm.com/api/getAsyncLocations?template=search&level=search&radius=100&search="
            + search_code
        )
        response = session.get(search_url, headers=headers).json()

        if response["markers"] is None:
            continue
        for location in response["markers"]:
            json_objects = extract_json(location["info"])[0]
            locator_domain = "mattressfirm.com"
            page_url = json_objects["url"]
            location_name = json_objects["location_name"]
            address = (
                json_objects["address_1"] + " " + json_objects["address_2"]
            ).strip()
            city = json_objects["city"]
            state = json_objects["region"]
            zipp = json_objects["post_code"]
            country_code = "US"

            phone = json_objects["local_phone"]
            location_type = json_objects["store_type_cs"].replace("Is", "").strip()

            latitude = json_objects["lat"]
            longitude = json_objects["lng"]
            store_number = json_objects["store_number"]

            if page_url in page_urls:
                continue

            counter = 0
            while True:
                counter = counter + 1
                if counter == 10:
                    raise Exception

                try:
                    hours_response = session.get(page_url, headers=headers).text

                except Exception:
                    continue

                if "location-title" in hours_response:
                    break

                else:
                    session = SgRequests(retry_behavior=None)
                    continue

            hours_soup = bs(hours_response, "html.parser")

            hours_parts = hours_soup.find_all("div", attrs={"class": "day-hour-row"})

            hours = ""
            for part in hours_parts:
                day = part.find("span", attrs={"class": "daypart"}).text.strip()
                hour = part.find("span", attrs={"class": "time"}).text.strip()
                hours = hours + day + " " + hour + ", "

            hours = hours[:-2].replace("\n", "").replace("\t", "").replace("\r", "")
            while "  " in hours:
                hours = hours.replace("  ", " ")

            hours = hours.strip()
            if len(hours_parts) == 0:
                raise Exception

            page_urls.append(page_url)

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
        latitude=sp.MappingField(mapping=["latitude"], is_required=False),
        longitude=sp.MappingField(mapping=["longitude"], is_required=False),
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
