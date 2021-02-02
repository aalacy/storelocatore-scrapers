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
    base_url = "https://www.schewels.com"
    res = session.get("https://www.schewels.com/store_finder.html")
    store_list = json.loads(
        res.text.split("var locations = ")[1]
        .split(";")[0]
        .replace("\n", "")
        .replace("\t", "")[:-2]
        + "]"
    )
    data = []
    for store in store_list:
        page_url = base_url + store["url"]
        street_address = store["address"]
        location_name = store["store_name"]
        city = store["city"]
        zip = store["zip"]
        state = store["state"]
        country_code = "US"
        latitude = store["latitude"]
        longitude = store["longitude"]
        location_type = "<MISSING>"
        store_number = "<MISSING>"

        res1 = session.get(page_url)
        soup1 = bs(res1.text, "lxml")

        try:
            phone = (
                soup1.select_one("div#location-phone-section")
                .text.replace("\t", "")
                .replace("\n", "")
            )
        except:
            phone = "<MISSING>"

        hours_of_operation = (
            soup1.select_one("div#location-hours-section table")
            .text.replace("\t", "")
            .replace("\n", " ")
        )

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
