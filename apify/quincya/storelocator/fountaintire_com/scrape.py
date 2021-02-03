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

    base_link = "https://www.fountaintire.com/umbraco/api/locations/get"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    # Request post
    payload = {
        "latitude": "51.253775",
        "longitude": "-85.323214",
        "radius": "5000",
        "services": "",
    }

    req = session.post(base_link, headers=headers, data=payload)
    base = BeautifulSoup(req.text, "lxml")
    js = base.text
    store_data = json.loads(js)

    data = []
    for store in store_data:
        final_link = "https://www.fountaintire.com/stores/details/" + store["id"]
        locator_domain = "fountaintire.com"

        location_name = store["branchName"]
        street_address = store["address"]
        city = store["city"].upper()
        state = store["province"]
        zip_code = store["postalCode"]
        country_code = "CA"
        store_number = store["id"]
        location_type = "<MISSING>"
        phone = store["phoneNumber"]

        hours_of_operation = ""
        raw_hours = store["deserializedHours"]
        days = ["Mon:", "Tue:", "Wed:", "Thu:", "Fri:", "Sat:", "Sun:"]

        for i, hours in enumerate(raw_hours):
            hours_of_operation = (
                hours_of_operation + " " + days[i] + " " + hours
            ).strip()

        latitude = store["lat"]
        longitude = store["lng"]
        data.append(
            [
                locator_domain,
                final_link,
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
