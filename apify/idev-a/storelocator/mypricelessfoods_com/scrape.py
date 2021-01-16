import csv
import json
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
    base_url = "https://www.mypricelessfoods.com/"
    res = session.get(
        "https://api.freshop.com/1/stores?app_key=priceless&has_address=true&limit=-1&token=08689a1502a6edf9abdb039719f9c7cb",
    )
    store_list = json.loads(res.text)["items"]
    data = []

    for store in store_list:
        store_number = store["store_number"]
        city = store["city"]
        state = store["state"]
        page_url = store["url"] if "url" in store.keys() else "<MISSING>"
        hours_of_operation = (
            store["hours_md"] if "hours_md" in store.keys() else "<MISSING>"
        )
        location_name = store["name"]
        street_address = (
            store["address_1"]
            if "address_1" in store.keys()
            else (store["address_0"] if "address_0" in store.keys() else "<MISSING>")
        )
        zip = store["postal_code"]
        country_code = store["country"] if "country" in store.keys() else "<MISSING>"
        phone = store["phone"] if "phone" in store.keys() else "<MISSING>"
        location_type = "<MISSING>"
        latitude = store["latitude"]
        longitude = store["longitude"]

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
