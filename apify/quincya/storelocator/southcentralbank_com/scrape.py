import csv
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

    base_link = "https://www.southcentralbank.com/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMoxR0gEJFGeUFni6FAPFomOBAsmlxSX5uW6ZqTkpELFapVoABU0Wug"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    store_data = session.get(base_link, headers=headers).json()["markers"]

    data = []
    locator_domain = "southcentralbank.com"

    for store in store_data:
        location_name = store["title"].upper()

        raw_data = BeautifulSoup(store["description"], "lxml")
        raw_address = list(raw_data.stripped_strings)[:2]

        street_address = raw_address[0].strip()
        city = raw_address[1].split(",")[0]
        state = raw_address[1].split(",")[1].split()[0]
        zip_code = raw_address[1].split(",")[1].split()[1]
        country_code = "US"
        store_number = store["id"]
        location_type = "<MISSING>"

        try:
            phone = re.findall(r"[(\d)]{3}-[\d]{3}-[\d]{4}", store["description"])[0]
        except:
            phone = "<MISSING>"

        hours_of_operation = "<MISSING>"
        rows = list(raw_data.stripped_strings)
        for i, row in enumerate(rows):
            if "hours" in row.lower():
                hours_of_operation = " ".join(rows[i:]).replace("ATM", "").strip().split("Drive")[0]
                break

        latitude = store["lat"]
        longitude = store["lng"]

        link = "https://www.southcentralbank.com/locations-and-team-members/"
        if store["link"]:
            link = ("https://www.southcentralbank.com" + store["link"]).replace(
                "locations", "locations-and-team-members"
            )
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
