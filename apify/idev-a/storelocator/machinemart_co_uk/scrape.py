import csv
import json
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

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
    base_url = "https://www.machinemart.co.uk"
    res = session.get(
        "https://www.machinemart.co.uk/customactions/storefindersurface/GetStores/"
    )
    store_list = json.loads(res.text)["Stores"]
    data = []

    for store in store_list:
        page_url = "https://www.machinemart.co.uk/stores/" + store["id"]
        location_name = store["name"]
        store_number = "<MISSING>"
        city = store["addressLine2"] or "<MISSING>"
        state = "<MISSING>"
        street_address = store["addressLine1"]
        zip = store["addressLine4"]
        country_code = "<MISSING>"
        phone = store["telephoneNumber"].replace("\n", "")
        location_type = "<MISSING>"
        latitude = store["latitude"]
        longitude = store["longitude"]
        res1 = session.get(page_url)
        hours = bs(res1.text, "lxml").select_one("div.times p").contents[2:]
        hours = [x.string for x in hours if x.string is not None]
        hours_of_operation = " ".join(hours) or "<MISSING>"

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
