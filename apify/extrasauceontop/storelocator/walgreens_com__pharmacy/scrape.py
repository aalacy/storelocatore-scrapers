from sgrequests import SgRequests
import json
from sgscrape import simple_scraper_pipeline as sp
from bs4 import BeautifulSoup as bs
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import sglog


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
    log = sglog.SgLogSetup().get_logger(logger_name="walgreens")
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=50
    )
    session = SgRequests()

    for search_code in search:
        url = "https://www.walgreens.com/storelocator/find.jsp?searchCriteria=" + str(
            search_code
        )

        try:
            response = session.get(url).text
        except Exception:
            raise Exception(url)

        json_objects = extract_json(response)

        try:
            locations = json_objects[3]["storelist"]["results"]
        except Exception:
            continue

        for location in locations:
            locator_domain = "https://www.walgreens.com/"
            page_url = locator_domain + location["storeSeoUrl"]
            location_name = location["store"]["address"]["street"]
            latitude = location["latitude"]
            longitude = location["longitude"]
            search.found_location_at(latitude, longitude)
            city = location["store"]["address"]["city"]
            store_number = location["storeNumber"]
            address = location_name
            state = location["store"]["address"]["state"]
            zipp = location["store"]["address"]["zip"]
            phone = location["store"]["phone"]["number"]
            location_type = location["store"]["name"]
            country_code = "US"

            hours = "<LATER>"
            try:
                hours_response = session.get(page_url).text
                hours_soup = bs(hours_response, "html.parser")
                hours_parts = hours_soup.find(
                    "li", attrs={"class": "single-hours-lists"}
                ).find_all("ul")

                hours = ""
                for part in hours_parts:
                    day = part.find("li", attrs={"class": "day"}).text.strip()
                    time = part.find("li", attrs={"class": "time"}).text.strip()

                    hours = hours + day + " " + time + ", "

                hours = hours[:-2]
            except Exception:
                log.info(page_url)
                hours = "<MISSING>"
                if "temporarily closed" in hours_response.lower():
                    continue

                else:
                    raise Exception

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
