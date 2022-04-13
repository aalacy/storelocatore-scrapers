from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape import simple_scraper_pipeline as sp
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
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
        "authority": "www.multicare.org",
        "method": "GET",
        "scheme": "https",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "identity",
        "accept-language": "en-US,en;q=0.9",
        "cookie": "_gcl_au=1.1.327728800.1633174484; nmstat=bdec21ab-2e1d-e199-071c-6de386320ce3; _hjid=8a276a42-9809-4add-a9c9-dc91bd9adff4; _fbp=fb.1.1633174488955.1897730601; _mkto_trk=id:512-OWW-241&token:_mch-multicare.org-1633174488998-42476; _gid=GA1.2.2038359169.1633536584; www._km_id=tNbyFVLn9cuZFnVgKDmS0RVuQvYrQjDO; www._km_user_name=Zealous Orca; www._km_lead_collection=false; _ga_95Z1PX6SEZ=GS1.1.1633615387.13.1.1633615391.0; _ga=GA1.2.1660038917.1633174485; _gat_UA-4300991-1=1; _tq_id.TV-8154818163-1.389f=69205b1954d4f79c.1633174488.0.1633615405..; _hjIncludedInPageviewSample=1; _hjAbsoluteSessionInProgress=1; _hjIncludedInSessionSample=0",
        "referer": "https://www.multicare.org/find-a-location/?query=&searchloc=&coordinates=&locationType=15&sortBy=&radius=30",
        "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36",
    }

    hours_headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"
    }

    search = DynamicGeoSearch(country_codes=[SearchableCountries.USA])

    for search_lat, search_lon in search:
        x = 0
        while True:
            x = x + 1
            url = (
                "https://www.multicare.org/find-a-location/?query=&searchloc=&coordinates="
                + "47.61"
                + "%2C"
                + "-122.34"
                + "&locationType=&sortBy=&radius=&page_num="
                + str(x)
            )
            response = session.get(url, headers=headers).text
            if (
                "No results were found with the search criteria provided. Please try again or select one of the quicklink options above."
                in response
            ):
                break

            soup = bs(response, "html.parser")
            grids = soup.find_all("div", attrs={"class": "location-list-card"})
            for grid in grids:
                locator_domain = "multicare.org"
                page_url = grid.find("h2").find("a")["href"]
                location_name = grid.find("h2").text.strip()
                latitude = grid.find(
                    "div", attrs={"class": "note distance js-distance-calc"}
                )["data-latitude"]
                longitude = grid.find(
                    "div", attrs={"class": "note distance js-distance-calc"}
                )["data-longitude"]
                search.found_location_at(latitude, longitude)

                address_parts = grid.find(
                    "div", attrs={"class": "details"}
                ).text.strip()

                if len(address_parts.split(", ")) == 2:
                    city = address_parts.split(", ")[0].split(" ")[-1]
                    address = "".join(
                        part + " "
                        for part in address_parts.split(", ")[0].split(" ")[:-1]
                    )
                    state = address_parts.split(", ")[-1].split(" ")[0]
                    try:
                        zipp = address_parts.split(", ")[-1].split(" ")[1]
                    except Exception:
                        zipp = "<MISSING>"

                elif len(address_parts.split(", ")) > 2:
                    city = address_parts.split(", ")[-2].split(" ")[-1]

                    address = ""

                    for part in address_parts.split(", ")[:-1]:
                        address = address + part + ", "

                    address = address[:-2]

                    address = "".join(part + " " for part in address.split(" ")[:-1])

                    state = address_parts.split(", ")[-1].split(" ")[0]
                    try:
                        zipp = address_parts.split(", ")[-1].split(" ")[1]
                    except Exception:
                        zipp = "<MISSING>"

                else:
                    raise Exception
                address = address.strip()

                store_number = grid["data-mcid"]
                try:
                    phone_part = (
                        grid.find("div", attrs={"class": "contact"})
                        .find("a")["href"]
                        .replace("tel:", "")
                    )

                    phone = ""
                    for character in phone_part:
                        if character.isdigit() is True:
                            phone = phone + character

                except Exception:
                    phone = "<MISSING>"
                location_type = grid.find("b").text.strip()
                country_code = "US"

                hours = "<INACCESSIBLE>"

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

        break


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
        location_type=sp.MappingField(
            mapping=["location_type"], part_of_record_identity=True
        ),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=get_data,
        field_definitions=field_defs,
        log_stats_interval=15,
        duplicate_streak_failure_factor=1000,
    )
    pipeline.run()


scrape()
