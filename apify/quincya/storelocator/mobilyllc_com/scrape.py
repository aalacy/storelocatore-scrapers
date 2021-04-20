import csv
import json
import re

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

    base_link = "http://www.mobilyllc.com/wp-admin/admin-ajax.php?action=store_search&lat=29.7604267&lng=-95.3698028&search_radius=150&autoload=1"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    locator_domain = "mobilyllc.com"

    stores = json.loads(base.text.strip())

    for store in stores:
        location_name = "MobilyLLC - " + store["store"]
        street_address = store["address"].replace("(Buda Town Center)", "").strip()
        if street_address[-1:] == ",":
            street_address = street_address[:-1]
        city = store["city"]
        if "NEW HAVEN" in street_address:
            street_address = street_address.replace("NEW HAVEN", "").strip()
            city = "New Haven"
        state = store["state"]
        zip_code = store["zip"]
        country_code = "US"
        store_number = store["id"]
        location_type = "<MISSING>"
        phone = store["phone"]
        hours_of_operation = (
            store["hours"]
            .replace("day", "day ")
            .replace("PM", "PM ")
            .replace("AM", "AM ")
            .strip()
        )
        hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()
        latitude = store["lat"]
        longitude = store["lng"]
        link = store["permalink"]

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
