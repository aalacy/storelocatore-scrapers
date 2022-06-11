import csv
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = (
        "https://api.storerocket.io/api/user/MZponDn8DN/locations?radius=50&units=miles"
    )

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["results"]["locations"]

    data = []
    locator_domain = "norms.com"

    for store in stores:
        if "coming-soon" in str(store):
            continue
        location_name = "Norms - " + store["name"]
        street_address = store["display_address"].split(",")[0].strip()
        city = store["city"]
        state = store["state"]
        zip_code = store["postcode"]
        country_code = "US"
        store_number = store["id"]
        location_type = "<MISSING>"
        phone = re.findall(r"tel:[0-9]+", str(store))[0].replace("tel:", "")

        hours_of_operation = ""
        try:
            raw_hours = store["hours"]
            for day in raw_hours:
                hours_of_operation = (
                    hours_of_operation + " " + day + " " + raw_hours[day]
                ).strip()
        except:
            if "Open 24/7" in str(store["fields"]):
                hours_of_operation = "Open 24/7"
            else:
                hours_of_operation = "<MISSING>"
        latitude = store["lat"]
        longitude = store["lng"]
        link = BeautifulSoup(store["phone"], "lxml").a["href"]

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
