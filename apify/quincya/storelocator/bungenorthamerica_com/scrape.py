import csv
import json

from bs4 import BeautifulSoup

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(
            [
                "locator_domain",
                "page_url",
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
            ]
        )
        for row in data:
            writer.writerow(row)


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://www.bungenorthamerica.com/locations"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    all_scripts = base.find_all("script")
    for script in all_scripts:
        if "locations:" in str(script):
            script = str(script)
            break
    js = script.split("locations:")[1].split("  ")[0]
    stores = json.loads(js)

    data = []
    locator_domain = "bungenorthamerica.com"

    for store in stores:
        location_name = store["name"]
        street_address = (
            store["address_1"].strip() + " " + store["address_2"].strip()
        ).strip()
        city = store["city"]
        state = store["state"]
        zip_code = store["postal_code"]
        country_code = store["country"]
        store_number = store["id"]
        location_type = "<MISSING>"
        phone = store["phone"].strip()
        latitude = store["latitude"]
        longitude = store["longitude"]
        link = "https://www.bungenorthamerica.com/locations"
        hours_of_operation = "<MISSING>"
        # Store data
        data.append(
            [
                locator_domain,
                link,
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
            ]
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
