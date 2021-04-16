import csv
import json

from bs4 import BeautifulSoup

from sgrequests import SgRequests

import usaddress


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    base_link = "https://www.subzeroicecream.com/find-location/c/0"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    js = str(base.find(id="gb-app-state").contents[0]).replace("&q;", '"')
    stores = json.loads(js)[
        "https://api.goodbarber.net/front/get_items/1829070/27785536/?category_index=0&a;geoloc=1&a;per_page=48"
    ]["body"]["items"]

    data = []

    locator_domain = "subzeroicecream.com"

    for store in stores:
        location_name = store["title"]
        if "Coming Soon" in location_name:
            continue
        street_address = (
            store["address"].replace("a;", "").replace(", TX, USA", "").strip()
        )

        if "-" in location_name:
            raw_address = (
                location_name.replace("Square Worc", "Square, Worc")
                .replace("UT, Tra", "UT - Trav")
                .replace("Caney TX", "Caney, TX")
                .replace("(Henderson)", "Henderson")
                .split("-")[-2]
            )
        else:
            raw_address = (
                location_name.replace("Square Worc", "Square, Worc")
                .replace("UT, Tra", "UT - Trav")
                .replace("Caney TX", "Caney, TX")
            )

        address = usaddress.parse(raw_address)
        city = ""
        state = ""
        for addr in address:
            if addr[1] == "PlaceName":
                city += addr[0].replace(",", "") + " "
            elif addr[1] == "StateName":
                state = addr[0]

        if "Sarasota" in location_name:
            city = "Sarasota"
            state = "FL"
        if not city:
            city = location_name.split(",")[0].strip()
        if not state:
            state = location_name.split(",")[1].strip()

        city = (
            city.replace("Atlanta Park", "Atlanta")
            .replace("Rimrock Mall", "Billings")
            .replace("(Flagler)", "")
            .replace("Square", "")
            .replace("Mass", "")
            .replace("(Shadyside)", "")
            .strip()
        )
        street_address = (
            street_address.replace(city, "").replace("Shadyside", "").strip()
        )
        state = state.split("-")[0]
        zip_code = "<MISSING>"
        country_code = "US"
        store_number = store["id"]
        location_type = "<MISSING>"
        phone = store["phoneNumber"]
        if not phone:
            phone = "<MISSING>"
        hours_of_operation = "<MISSING>"
        latitude = store["latitude"]
        longitude = store["longitude"]
        link = store["url"]

        # Store data
        data.append(
            [
                locator_domain,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
                link,
            ]
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
