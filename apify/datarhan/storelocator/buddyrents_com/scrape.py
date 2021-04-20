import csv
import json
from lxml import etree

from sgselenium import SgFirefox


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
    items = []
    scraped_items = []

    DOMAIN = "buddyrents.com"
    start_url = "https://www.buddyrents.com/storelocator/storelocator_data.php?origLat=37.09024&origLng=-95.712891&origAddress=5000+Estate+Enighed%2C+Independence%2C+KS+67301%2C+%D0%A1%D0%A8%D0%90&formattedAddress=&boundsNorthEast=&boundsSouthWest="

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)
        data = dom.xpath('//div[@id="json"]/text()')[0]
        all_locations = json.loads(data)

    for poi in all_locations:
        store_url = poi["web"]
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]
        if poi["address2"]:
            street_address += " " + poi["address2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["postal"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["id"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["lng"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = f'{poi["hours1"]} {poi["hours2"]} {poi["hours3"]}'

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
        check = f"{location_name} {street_address}"
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
