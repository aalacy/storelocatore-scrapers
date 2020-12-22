import csv
import json

from bs4 import BeautifulSoup

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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

    base_link = "https://www.odeon.co.uk/cinemas/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find_all(class_="btn blue")[1:]
    locator_domain = "odeon.co.uk"

    items = json.loads(base.find(id="v-site-list-all-cinemas")["data-v-site-list"])[
        "config"
    ]["cinemas"]

    for item in items:

        link = "https://www.odeon.co.uk" + item["url"]
        location_name = item["name"]
        street_address = item["addressLine1"]
        city = item["addressLine2"]
        state = "<MISSING>"
        zip_code = item["postCode"]
        country_code = "GB"
        store_number = item["id"]
        if item["isImax"]:
            location_type = "IMAX"
        else:
            location_type = "Cinema"
        phone = "<MISSING>"
        hours_of_operation = "<MISSING>"
        latitude = item["latitude"]
        longitude = item["longitude"]

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
