import re
import csv
import json
from urllib.parse import urljoin

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

    start_url = "https://afsshareportal.com/lookUpFeatures.php?callback=jsonpcallbackHours&action=storeInfo&website_url=broulims.com&expandedHours=true"
    domain = "broulims.com"

    response = session.get(start_url)
    data = re.findall(r"jsonpcallbackHours\((.+)\)", response.text)[0]
    data = json.loads(data)

    for poi in data:
        poi = poi[0]
        location_name = poi["store_name"]
        store_url = urljoin(
            "https://broulims.com/",
            location_name.replace("Broulim's ", "").replace(" ", "_").lower(),
        )
        street_address = " ".join(poi["store_address"].split())
        city = poi["store_city"]
        state = poi["store_state"]
        zip_code = poi["store_zip"]
        country_code = "<MISSING>"
        store_number = poi["store_id"]
        phone = poi["store_phone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["store_department_name"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["store_lat"]
        longitude = poi["store_lng"]
        hoo = []
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        for day in days:
            hours = poi[day]
            hoo.append("{} {}".format(day, hours))
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
