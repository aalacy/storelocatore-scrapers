import re
import csv
import json
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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []

    DOMAIN = "saveonfoods.com"
    start_url = "https://www.saveonfoods.com/sm/pickup/rsid/987/store"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "PRELOADED_STATE__=")]/text()')[0]
    data = re.findall("PRELOADED_STATE__=(.+)", data)[0]
    data = json.loads(data)

    for poi in data["stores"]["allStores"]["items"]:
        store_url = "https://www.saveonfoods.com/sm/pickup/rsid/987/store"
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["addressLine1"]
        if poi["addressLine2"]:
            street_address += ", " + poi["addressLine2"]
        if poi["addressLine3"]:
            street_address += ", " + poi["addressLine3"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["countyProvinceState"]
        state = state if state else "<MISSING>"
        zip_code = poi["postCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["location"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["location"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = poi["openingHours"]
        if not hours_of_operation:
            details_url = (
                "https://storefrontgateway.saveonfoods.com/api/{}/attributes".format(
                    poi["id"]
                )
            )
            d_response = session.get(details_url)
            d_data = json.loads(d_response.text)
            d_data = json.loads(
                [
                    elem
                    for elem in d_data["attributes"]
                    if elem["name"] == "Departments"
                ][0]["value"]
            )
            weekdays = d_data["Pharmacy"]["Weekdays"]
            saturday = d_data["Pharmacy"]["Saturday"]
            sunday = d_data["Pharmacy"]["Sunday"]
            hours_of_operation = (
                f"Weekdays {weekdays}, Saturday {saturday}, Sunday {sunday}"
            )
        hours_of_operation = (
            hours_of_operation.replace(";", " ") if hours_of_operation else "<MISSING>"
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
