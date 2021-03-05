import csv
import json
from lxml import etree

from sgselenium.sgselenium import SgFirefox


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
    items = []

    DOMAIN = "fredmeyerjewelers.com"
    start_url = "https://www.fredmeyerjewelers.com/Service/storelocatorhandler.ashx?action=FindStores&location=10001&radius=10000&fromPg=other"
    with SgFirefox() as driver:
        driver.get(start_url)
        response_html = driver.page_source

    dom = etree.HTML(response_html)
    data = dom.xpath('//div[@id="json"]/text()')[0]
    all_poi = json.loads(data)
    for poi in all_poi:
        store_url = "<MISSING>"
        location_name = poi["StoreName"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["AddressLine1"]
        if poi["AddressLine2"]:
            street_address += ", " + poi["AddressLine2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["City"]
        city = city if city else "<MISSING>"
        state = poi["State"]
        state = state if state else "<MISSING>"
        zip_code = poi["ZipCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["StoreNumber"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["Phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["Latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["Longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        hours_dict = {}
        for name, hours in poi["StoreHours"].items():
            day = name.replace("Open", "").replace("Close", "")
            if not hours_dict.get(day):
                hours_dict[day] = {}
            if "Open" in name:
                hours_dict[day]["open"] = hours
            else:
                hours_dict[day]["close"] = hours
        for day, hours in hours_dict.items():
            hours_of_operation.append(
                "{} {} - {}".format(day, hours["open"], hours["close"])
            )
        hours_of_operation = (
            ", ".join(hours_of_operation) if hours_of_operation else "<MISSING"
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
