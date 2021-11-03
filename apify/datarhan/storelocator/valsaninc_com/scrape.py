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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://www.powr.io/cached/22676543.json"
    domain = "valsaninc.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr).json()

    all_locations = response["content"]["locations"]
    for poi in all_locations:
        store_url = "https://www.valsaninc.com/pages/store-locator"
        location_name = poi["name"]
        raw_address = poi["address"].split(", ")
        if len(raw_address) == 5:
            raw_address = [", ".join(raw_address[:2])] + raw_address[2:]
        street_address = raw_address[0]
        street_address = street_address.replace("West Sunset Square, ", "")
        city = raw_address[1]
        state = raw_address[2].split()[0]
        zip_code = raw_address[2].split()[-1]
        country_code = raw_address[-1].strip()
        if country_code == "EE. UU.":
            country_code = "USA"
        store_number = "<MISSING>"
        phone = poi["number"]
        location_type = "<MISSING>"
        latitude = poi["lat"]
        longitude = poi["lng"]
        hoo = poi["description"].split()
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
