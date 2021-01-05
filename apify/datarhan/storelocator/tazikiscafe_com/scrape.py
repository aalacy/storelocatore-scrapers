import csv
import json

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
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "tazikiscafe.com"
    start_url = "https://api2.storepoint.co/v1/15a6f4ccb641d3/locations?lat=40.551761627197266&long=-74.46468353271484&radius=5000"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["results"]["locations"]:
        store_url = poi["website"]
        location_name = poi["name"]
        raw_address = poi["streetaddress"].split(", ")
        if len(raw_address) == 5:
            raw_address = [", ".join(raw_address[:2])] + raw_address[2:]
        street_address = raw_address[0]
        city = raw_address[1]
        state = raw_address[2].split()[0]
        zip_code = raw_address[2].split()[-1]
        country_code = raw_address[-1]
        store_number = poi["id"]
        location_type = "<MISSING>"
        phone = poi["phone"]
        latitude = poi["loc_lat"]
        longitude = poi["loc_long"]
        hours_of_operation = []
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        for day in days:
            hours_of_operation.append("{} {}".format(day, poi[day]))
        hours_of_operation = " ".join(hours_of_operation)

        if "Temporarily Closed" in location_name:
            hours_of_operation = "Temporarily Closed"

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

        check = "{} {}".format(street_address, location_name)
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
