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

    base_link = "https://www.bncollege.com/campus-stores/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    script = (
        base.find(id="bnc-map-js-extra")
        .text.split("bncLocationsByState = ")[1]
        .split("]};")[0]
        + "]}"
    )

    states = json.loads(script)
    locator_domain = "bncollege.com"

    for i in states:
        stores = states[i]
        for store in stores:
            location_name = store["title"]
            country_code = "US"
            raw_address = store["address"].replace(",", "\n").split("\n")
            city = raw_address[-2].strip()
            if "Bahamas" in city:
                continue
            street_address = (
                (
                    store["address"][: store["address"].rfind(city)]
                    .replace("\n", " ")
                    .strip()
                )
                .replace("  ", " ")
                .replace("Ivy Tech Community College - Illinois Fall Creek Center", "")
                .strip()
            )
            if street_address[-1:] == ",":
                street_address = street_address[:-1].strip()

            if location_name == "Hanover College":
                street_address = "One Campus Dr"

            if location_name == "Hartwick College":
                street_address = "1 Hartwick Drive Dewar Hall, 3rd Flr"

            if location_name == "Cuesta College San Luis Obispo Campus":
                street_address = "-1"
                city = "San Luis Obispo"

            if "530 S. State Street" in city:
                street_address = "530 S. State Street"
                city = "Ann Arbor"

            if "1300 nevada state drive" in city:
                street_address = "1300 nevada state drive"
                city = "Henderson"

            if "1 Saxton Drive" in city:
                street_address = "1 Saxton Drive"
                city = "Alfred"

            if "Liverpool L69 3BX" in city:
                city = "Liverpool"
                zip_code = "L69 3BX"
                country_code = "UK"

            if "210 Cowan Blvd" in street_address:
                country_code = "CA"
                zip_code = "N1T 1V4"

            if "versity of St Francis Fort" in street_address:
                street_address = street_address.split("Fort")[0].strip()

            if not street_address:
                street_address = "<MISSING>"

            state = store["state_code"].upper()
            zip_code = store["address"][store["address"].rfind(state) + 2 :].strip()
            if not zip_code.isdigit() and country_code == "US":
                zip_code = "<MISSING>"
            store_number = store["id"]
            location_type = ", ".join(store["types"])

            if not location_type:
                location_type = "<MISSING>"

            phone = store["phone"]
            hours_of_operation = "<INACCESSIBLE>"
            latitude = store["lat"]
            longitude = store["lng"]
            page_url = store["url"]

            data.append(
                [
                    locator_domain,
                    page_url,
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
