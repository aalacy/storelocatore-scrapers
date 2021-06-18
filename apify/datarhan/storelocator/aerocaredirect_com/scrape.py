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

    start_url = (
        "https://storerocket.global.ssl.fastly.net/api/user/WLy8GYO4r0/locations"
    )
    domain = "aerocaredirect.com"

    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()

    all_locations = data["results"]["locations"]
    for poi in all_locations:
        store_url = (
            f'https://aerocaredirect.com/pages/store-locator?location={poi["obf_id"]}'
        )
        location_name = poi["name"]
        street_address = poi["display_address"]
        if street_address.endswith(","):
            street_address = street_address[:-1]
        city = poi["city"]
        state = poi["state"]
        zip_code = poi["postcode"]
        country_code = poi["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["id"]
        phone = ""
        if poi.get("fields"):
            phone = poi["fields"][0]["pivot_field_value"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["locationType"]["name"]
        latitude = poi["lat"]
        longitude = poi["lng"]
        hours_of_operation = "<MISSING>"

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
