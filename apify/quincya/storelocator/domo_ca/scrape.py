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

    base_link = "https://www.domo.ca/wp-json/wpgmza/v1/markers/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMoxR0gEJFGeUgsSKgYLRsbVKtQCV7hBN"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()

    data = []
    locator_domain = "domo.ca"

    for store in stores:
        location_name = store["title"].replace("\\", "")
        raw_data = list(
            BeautifulSoup(
                store["description"]
                .replace("St, Del", "St Del")
                .replace("\n", " ")
                .replace("45, 99", "45 99"),
                "lxml",
            ).stripped_strings
        )

        if not store["description"]:
            raw_data = store["address"].replace("peg, MB", "peg MB").split(",")
            raw_data[1] = raw_data[1].replace("peg MB", "peg, MB")

        if "," in raw_data[1]:
            street_num = 0
            city_num = 1
        else:
            street_num = 1
            city_num = 2

        street_address = raw_data[street_num]
        if ", " in raw_data[0]:
            street_address = "<MISSING>"
            city_num = 0
        city = raw_data[city_num].split(",")[0].strip()
        state = raw_data[city_num].split(",")[1].replace(".", "").strip()
        zip_code = "<MISSING>"

        country_code = "CA"
        location_type = "<MISSING>"

        try:
            phone = re.findall(r"[(\d)]{5} [\d]{3}-[\d]{4}", store["description"])[0]
        except:
            phone = "<MISSING>"

        hours_of_operation = "<MISSING>"
        latitude = store["lat"]
        longitude = store["lng"]
        store_number = store["id"]
        # Store data
        data.append(
            [
                locator_domain,
                "https://www.domo.ca/locations/",
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
