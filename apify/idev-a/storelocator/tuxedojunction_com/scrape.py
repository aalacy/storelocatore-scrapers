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
    base_url = "https://www.tuxedojunction.com/"
    payload = {
        "distance": "2529.041861523396",
        "lat": "38.79263436096801",
        "lng": "-93.5444122625",
        "rad": "2529.041861523396",
        "action": "get_stores",
    }
    res = session.post(
        "https://www.tuxedojunction.com/wp-admin/admin-ajax.php", data=payload
    )
    store_list = json.loads(res.text)
    data = []
    for store in store_list:
        page_url = "https://www.tuxedojunction.com/stores"
        street_address = store["address_1"]
        location_name = store["dba"]
        city = store["city"]
        zip = store["postcode"]
        state = store["state"]
        country_code = "US"
        latitude = store["lat"]
        longitude = store["long"]
        location_type = "<MISSING>"
        store_number = store["store_number"]
        phone = store["phone"]
        hours_of_operation = (
            bs(store["store_hours"], "lxml").select_one("body").text
            if "store_hours" in store.keys() and store["store_hours"] != ""
            else "<MISSING>"
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
