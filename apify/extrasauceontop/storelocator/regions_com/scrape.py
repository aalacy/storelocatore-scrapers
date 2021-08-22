import re
import json
from sgrequests import SgRequests
import pandas as pd
from bs4 import BeautifulSoup as bs
from sgzip.static import static_zipcode_list, SearchableCountries
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

    session = SgRequests()
    search = static_zipcode_list(country_code=SearchableCountries.USA, radius=30)

    locator_domains = []
    page_urls = []
    location_names = []
    street_addresses = []
    citys = []
    states = []
    zips = []
    country_codes = []
    store_numbers = []
    phones = []
    location_types = []
    latitudes = []
    longitudes = []
    hours_of_operations = []

    for search_code in search:
        url = (
            "https://www.regions.com/Locator?regions-get-directions-starting-coords=&daddr=&autocompleteAddLat=&autocompleteAddLng=&r=&geoLocation="
            + search_code
            + "&type=branch"
        )
        response = session.get(url).text

        json_objects = extract_json(response)
        for location in json_objects:
            if "title" not in location.keys():
                continue

            locator_domain = "regions.com"
            location_name = location["title"]
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
            location_type = location["type"]
            latitude = location["lat"]
            longitude = location["lng"]

            locator_domains.append(locator_domain)
            location_names.append(location_name)
            street_addresses.append(address)
            citys.append(city)
            states.append(state)
            zips.append(zipp)
            country_codes.append(country_code)
            location_types.append(location_type)
            latitudes.append(latitude)
            longitudes.append(longitude)
            store_numbers.append(store_number)

        soup = bs(response, "html.parser")

        grids = soup.find_all("li", attrs={"class": "locator-result__list-item"})

        for grid in grids:
            a_tag = grid.find("a")
            try:
                page_url = "regions.com" + a_tag["href"]
            except Exception:
                page_url = "<MISSING>"
            page_urls.append(page_url)

    df = pd.DataFrame(
        {
            "locator_domain": locator_domains,
            "page_url": page_urls,
            "location_name": location_names,
            "street_address": street_addresses,
            "city": citys,
            "state": states,
            "zip": zips,
            "store_number": store_numbers,
            "latitude": latitudes,
            "longitude": longitudes,
            "country_code": country_codes,
            "location_type": location_types,
        }
    )

    df["dupecheck"] = (
        df["location_name"]
        + df["street_address"]
        + df["city"]
        + df["state"]
        + df["location_type"]
    )

    df = df.drop_duplicates(subset=["dupecheck"])
    df = df.drop(columns=["dupecheck"])

    for row in df.iterrows():
        hours = "<MISSING>"
        phone = "<MISSING>"
        if row[1]["location_type"] == "branch" and row[1]["page_url"] != "<MISSING>":
            response = session.get("https://" + row[1]["page_url"]).text
            json_objects = extract_json(response)

            for item in json_objects:
                if "name" not in item.keys():
                    continue
                else:
                    try:
                        phone = item["telephone"].replace("+", "")
                    except Exception:
                        pass

                    hours = ""
                    try:
                        for part in item["openingHoursSpecification"]["dayOfWeek"]:
                            for day in part["dayOfWeek"]:
                                if part["opens"] == part["closes"]:
                                    hours = hours + day + " closed, "
                                else:
                                    hours = (
                                        hours
                                        + day
                                        + " "
                                        + part["opens"]
                                        + " - "
                                        + part["closes"]
                                        + ", "
                                    )

                    except Exception:
                        pass

                    break

        if hours != "<MISSING>":
            hours = hours[:-2]
        hours_of_operations.append(hours)
        phones.append(phone)

    df["phone"] = phones
    df["hours_of_operation"] = hours_of_operations

    for row in df.iterrows():

        yield {
            "locator_domain": row[1]["locator_domain"],
            "page_url": row[1]["page_url"],
            "location_name": row[1]["location_name"],
            "latitude": row[1]["latitude"],
            "longitude": row[1]["longitude"],
            "city": row[1]["city"],
            "store_number": row[1]["store_number"],
            "street_address": row[1]["street_address"],
            "state": row[1]["state"],
            "zip": row[1]["zip"],
            "phone": row[1]["phone"],
            "location_type": row[1]["location_type"],
            "hours": row[1]["hours_of_operation"],
            "country_code": row[1]["country_code"],
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
