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

    start_url = "https://www.mastermechanic.ca/locations/data/locations.php?origAddress=554+Lansdowne+St%2C+Peterborough%2C+ON+K9J+3R8%2C+%D0%9A%D0%B0%D0%BD%D0%B0%D0%B4%D0%B0"
    domain = "mastermechanic.ca"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_locations = session.get(start_url, headers=hdr).json()

    for poi in all_locations:
        store_url = "https://www.mastermechanic.ca/locations/"
        location_name = poi["name"]
        street_address = poi["address"]
        city = poi["city"]
        state = poi["state"]
        zip_code = poi["postal"]
        country_code = "<MISSING>"
        store_number = poi["store_id"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        longitude = poi["lng"]
        hoo = []
        for d, h in poi.items():
            if d in ["hours_today", "hours_note"]:
                continue
            if "hours_" in d:
                day = d.split("_")[-1]
                hours = h.strip()
                hoo.append(f"{day} {hours}")
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
