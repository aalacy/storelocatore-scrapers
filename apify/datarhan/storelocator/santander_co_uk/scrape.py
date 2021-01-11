import re
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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    DOMAIN = "santander.com"
    start_url = "https://back-scus.azurewebsites.net/branch-locator/find/gb?config=%7B%22coords%22%3A%5B51.5150432%2C-0.1020399%5D%7D&northEast=51.559354602729734%2C0.11768666250002724&southWest=51.47068864934726%2C-0.32176646249999274&callback=angular.callbacks._2"

    response = session.get(start_url)
    data = re.findall(r"._2\((.+?)\);", response.text)[0]
    data = json.loads(data)

    for poi in data:
        store_url = poi["urlDetailPage"]
        location_name = poi["name"]
        city = poi["location"]["city"]
        street_address = poi["location"]["address"].split(city)[0][:-2]
        state = poi["location"]["address"].split(", ")[-2]
        zip_code = poi["location"]["zipcode"]
        country_code = poi["location"]["country"]
        if country_code != "UK":
            continue
        store_number = poi["poicode"]
        phone = "<MISSING>"
        location_type = poi["objectType"]["code"]
        latitude = poi["location"]["coordinates"][1]
        longitude = poi["location"]["coordinates"][0]
        hours_of_operation = "<MISSING>"

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
