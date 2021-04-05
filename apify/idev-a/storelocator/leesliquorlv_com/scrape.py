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
    base_url = "https://leesliquorlv.com"
    res = session.get(
        "https://leesliquorlv.com/wp-admin/admin-ajax.php?action=store_search&lat=36.1118199&lng=-115.2415347&max_results=100&search_radius=500&autoload=1",
    )
    store_list = json.loads(res.text)
    data = []
    for store in store_list:
        store_number = store["id"]
        city = store["city"]
        state = store["state"]
        page_url = store["permalink"]
        soup = bs(store["hours"], "lxml")
        hours_of_operation = soup.text.replace("\n", " ").replace("–", "-")
        location_name = store["store"].replace("&#038;", "&")
        street_address = store["address"]
        zip = store["zip"]
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
