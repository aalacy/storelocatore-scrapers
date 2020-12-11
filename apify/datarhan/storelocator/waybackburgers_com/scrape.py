import csv
import urllib.parse
from lxml import etree
from sgselenium import SgFirefox


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

    DOMAIN = "waybackburgers.com"
    start_url = "https://waybackburgers.com/locations/"

    all_locations = []
    with SgFirefox() as driver:
        driver.get(start_url)
        driver_r = etree.HTML(driver.page_source)
    all_locations = driver_r.xpath('//li[@class="locations_list_item "]')

    for poi in all_locations:
        store_url = poi.xpath("@data-order_online_url")
        store_url = store_url[0] if store_url[0].strip() else "<MISSING>"
        if store_url == "<MISSING>":
            store_url = (
                "https://waybackburgers.com/locations/#location_"
                + poi.xpath("@data-id")[0]
            )
        location_name = poi.xpath("@data-name")
        location_name = (
            urllib.parse.unquote(location_name[0]) if location_name else "<MISSING>"
        )
        street_address = poi.xpath("@data-address")
        street_address = (
            urllib.parse.unquote(street_address[0]).replace("\n", "")
            if street_address
            else "<MISSING>"
        )
        city = poi.xpath("@data-city")
        city = urllib.parse.unquote(city[0]) if city else "<MISSING>"
        state = poi.xpath("@data-state")
        state = state[0] if state else "<MISSING>"
        zip_code = poi.xpath("@data-postal_code")
        zip_code = urllib.parse.unquote(zip_code[0]) if zip_code else "<MISSING>"
        country_code = poi.xpath("@data-country")
        country_code = country_code[0].strip() if country_code else "<MISSING>"
        if country_code not in ["USA", "Canada"]:
            continue
        store_number = poi.xpath("@data-id")
        store_number = store_number[0] if store_number else "<MISSING>"
        phone = poi.xpath("@data-phone")
        phone = urllib.parse.unquote(phone[0]) if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi.xpath("@data-geo_latitude")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = poi.xpath("@data-geo_longitude")
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = urllib.parse.unquote(poi.xpath("@data-hours")[0])
        hours_html = etree.HTML(hours_of_operation)
        hours_of_operation = " ".join(hours_html.xpath(".//text()"))

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
