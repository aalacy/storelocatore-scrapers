import re
import json
from sgrequests import SgRequests
import pandas as pd
from bs4 import BeautifulSoup as bs
from sgzip.static import static_zipcode_list, SearchableCountries


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
                        phone = item["telephone"]
                    except Exception:
                        pass

                    try:
                        hours = ""
                        for piece in item["department"][0]["openingHours"]:
                            hours = hours + piece + ", "
                        hours = hours[:-2]

                        if hours == "Mo  - Su Closed":
                            hours = ""
                            for piece in item["department"][1]["openingHours"]:
                                hours = hours + piece + ", "
                            hours = hours[:-2]
                    except Exception:
                        pass
                    break

        hours_of_operations.append(hours)
        phones.append(phone)

    df["phone"] = phones
    df["hours_of_operation"] = hours_of_operations

    return df


def write_data(df):
    df = df.fillna("<MISSING>")
    df = df.replace(r"^\s*$", "<MISSING>", regex=True)

    df["dupecheck"] = (
        df["location_name"]
        + df["street_address"]
        + df["city"]
        + df["state"]
        + df["location_type"]
    )

    df = df.drop_duplicates(subset=["dupecheck"])
    df = df.drop(columns=["dupecheck"])
    df = df.replace(r"^\s*$", "<MISSING>", regex=True)
    df = df.fillna("<MISSING>")

    df.to_csv("data.csv", index=False)


df = get_data()
write_data(df)
