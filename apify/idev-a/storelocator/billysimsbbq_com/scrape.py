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
    base_url = "https://billysimsbbq.com"
    res = session.get(
        "https://billysimsbbq.com/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=e8904e9c7a&load_all=1&layout=1",
    )
    store_list = json.loads(res.text)
    data = []

    for store in store_list:
        store_number = store["id"]
        city = store["city"]
        state = store["state"].split(",")[0]
        page_url = store["website"]
        hours = json.loads(store["open_hours"])
        hours_of_operation = ""
        for x in hours:
            if hours[x] == "0":
                hours_of_operation += x + " Closed "
            else:
                hours_of_operation += x + " " + ", ".join(hours[x]) + " "
        location_name = store["title"]
        street_address = store["street"]
        zip = store["postal_code"]
        country_code = store["country"]
        phone = store["phone"]
        location_type = "<MISSING>"
        latitude = store["lat"]
        longitude = store["lng"]

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
