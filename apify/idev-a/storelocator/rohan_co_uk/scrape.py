import csv
import json
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests

session = SgRequests()


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
    base_url = "https://www.rohan.co.uk"
    res = session.get(
        "https://www.rohan.co.uk/home/shopfinder/all",
    )
    region_list = json.loads(
        res.text.split("areas = ")[1].split("initPostcode = ")[0].strip()[:-1]
    )
    data = []
    for region in region_list:
        for store in region["Stores"]:
            location_name = store["Name"]
            address = bs(store["Address"], "lxml").select("li")
            address = [x.string for x in address]
            zip = address.pop()
            city = address.pop()
            state = "<MISSING>"
            street_address = " ".join(address).replace("’", "'")
            page_url = base_url + store["Url"]
            country_code = "UK"
            phone = store["TelephoneNumber"]
            store_number = "<MISSING>"
            location_type = "<MISSING>"
            latitude = store["Latitude"]
            longitude = store["Longitude"]
            hours = bs(store["Info"], "lxml").select("ul").pop().select("li")
            hours = [x.string for x in hours]
            hours_of_operation = (
                " ".join(hours)
                .replace("<BR>", " ")
                .replace("<br>", " ")
                .replace("–", "-")
                or "<MISSING>"
            )
            if "Permanently" in hours_of_operation:
                continue

            data.append(
                [
                    base_url,
                    page_url,
                    location_name,
                    street_address,
                    city,
                    state,
                    zip,
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


if __name__ == "__main__":
    scrape()
