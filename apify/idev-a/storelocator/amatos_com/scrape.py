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
    base_url = "https://www.amatos.com/"
    res = session.post(
        "https://www.amatos.com/wp-admin/admin-ajax.php?action=store_search&lat=43.6541567&lng=-70.2802294&max_results=75&search_radius=500&autoload=1",
    )
    store_list = json.loads(res.text)
    data = []

    for store in store_list:
        store_number = store["id"]
        city = store["city"]
        state = store["state"]
        page_url = store["permalink"]
        hours_of_operation = " ".join(store["wpsl_hours"].split('"')[1::2])

        street_address = store["address"]
        location_name = (
            store["store"].replace("&#8217;", "'").replace(store["state"], "").strip()
        )
        location_name = (
            location_name[:-1] if location_name.endswith(",") else location_name
        )
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
