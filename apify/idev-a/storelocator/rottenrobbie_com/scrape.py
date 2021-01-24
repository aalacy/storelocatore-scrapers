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
    base_url = "https://www.rottenrobbie.com"
    res = session.get(
        "https://www.rottenrobbie.com/wp/wp-admin/admin-ajax.php?action=store_search&lat=36.77826&lng=-119.41793&max_results=100&search_radius=300&autoload=1"
    )
    store_list = json.loads(res.text)
    data = []
    for store in store_list:
        page_url = "https://www.rottenrobbie.com/locations/"
        location_name = store["store"]
        street_address = store["address"]
        city = store["city"]
        state = store["state"]
        zip = store["zip"]
        country_code = store["country"] or "<MISSING>"
        phone = store["phone"] or "<MISSING>"
        location_type = "<MISSING>"
        store_number = store["id"]
        latitude = store["lat"]
        longitude = store["lng"]
        hours_of_operation = "<MISSING>"

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
