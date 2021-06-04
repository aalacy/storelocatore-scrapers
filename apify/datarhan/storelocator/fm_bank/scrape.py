import re
import csv

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
    # Your scraper here
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://www.fm.bank/wp-admin/admin-ajax.php?action=store_search&lat=41.52144&lng=-84.30717&max_results=50&search_radius=100&autoload=1"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")

    all_locations = session.get(start_url).json()
    for poi in all_locations:
        store_url = "https://www.fm.bank/locations/"
        location_name = poi["store"]
        location_name = (
            location_name.replace("&#8211;", "-")
            .replace("#038;", "")
            .replace("&#8217;", "'")
            if location_name
            else "<MISSING>"
        )
        street_address = poi["address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["id"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["cat_name"]
        latitude = poi["lat"]
        longitude = poi["lng"]
        hoo = [
            poi["lobby_hours_l1"],
            poi["lobby_hours_v1"],
            poi["lobby_hours_l2"],
            poi["lobby_hours_v2"],
            poi["lobby_hours_l3"],
            poi["lobby_hours_v3"],
            poi["lobby_hours_l4"],
            poi["lobby_hours_v4"],
        ]
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        item = [
            domain,
            store_url,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
