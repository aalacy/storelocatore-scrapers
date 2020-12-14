import csv
import json
from sgrequests import SgRequests


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
    # Your scraper here
    session = SgRequests()

    items = []

    DOMAIN = "motionindustries.com"
    start_urls = [
        "https://www.motionindustries.com/misvc/mi/services/json/locations.search?siteCode=MI",
        "https://www.motionindustries.com/misvc/mi/services/json/locations.search?corpCode=2&searchType=1&siteCode=MI",
    ]

    all_poi = []
    for url in start_urls:
        response = session.get(url)
        data = json.loads(response.text)
        all_poi += data["locations"]

    for poi in all_poi:
        store_url = "<MISSING>"
        location_name = poi["label"]
        street_address = poi["addrLine2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        for elem in poi["openCloseTimes"]:
            if elem["closeTime"] == "Closed":
                hours_of_operation.append("{} closed".format(elem["dayOfWeek"]))
            elif not elem["openTime"]:
                hours_of_operation.append("{} closed".format(elem["dayOfWeek"]))
            else:
                hours_of_operation.append(
                    "{} {} - {}".format(
                        elem["dayOfWeek"], elem["openTime"], elem["closeTime"]
                    )
                )
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

        item = [
            DOMAIN,
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
