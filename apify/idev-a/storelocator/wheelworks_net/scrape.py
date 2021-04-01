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
    base_url = "https://www.wheelworks.net"
    res = session.get(
        "https://www.wheelworks.net/bsro/services/store/location/get-list-by-zip?zipCode=94509",
    )
    store_list = json.loads(res.text)["data"]["stores"]
    data = []
    for store in store_list:
        page_url = store["localPageURL"]
        location_name = store["storeName"]
        street_address = store["address"]
        city = store["city"]
        state = store["state"]
        zip = store["zip"]
        country_code = "<MISSING>"
        phone = store["phone"] or "<MISSING>"
        location_type = store["storeType"]
        store_number = store["storeNumber"]
        latitude = store["latitude"]
        longitude = store["longitude"]
        hours_of_operation = ""
        for x in store["hours"]:
            hours_of_operation += (
                x["weekDay"] + ": " + x["openTime"] + "-" + x["closeTime"] + " "
            )
        hours_of_operation = hours_of_operation.strip()

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
