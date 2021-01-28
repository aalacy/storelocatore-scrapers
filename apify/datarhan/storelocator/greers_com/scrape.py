import re
import csv
import demjson
from lxml import etree

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

    DOMAIN = "greers.com"
    start_url = "https://www.greers.com/storelocator"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "data =")]/text()')[0]
    data = re.findall("data = (.+)", data.replace("\n", ""))[0][:-1]
    data = demjson.decode(data)

    for poi in data["StoreList"]:
        store_url = "<MISSING>"
        location_name = poi["StoreName"]
        street_address = poi["PrimaryAddress"]
        location_type = "<MISSING>"
        city = poi["City"]
        state = poi["StateName"]
        zip_code = poi["PostalCode"]
        country_code = "<MISSING>"
        store_number = poi["StoreNumber"]
        phone = poi["Phone"].split()[0]
        phone = phone if phone else "<MISSING>"
        latitude = poi["Latitude"]
        longitude = poi["Longitude"]
        hours_of_operation = poi["OpenHoursDisplay"]

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
