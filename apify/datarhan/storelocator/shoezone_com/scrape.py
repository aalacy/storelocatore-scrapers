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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    DOMAIN = "shoezone.com"
    start_url = "https://www.shoezone.com/Stores"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath(
        '//div[contains(@class, "stores")]//a[contains(@href, "Stores")]/@href'
    )

    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath('//input[@id="ctl00_mainContent_hidStoreJSON"]/@value')[0]
        poi = json.loads(poi)

        location_name = poi["Name"]
        location_name = location_name if location_name else "<MISSING>"
        if len(poi["Address"].split(",")) == 3:
            street_address = ", ".join(poi["Address"].split(",")[:-1])
        else:
            street_address = poi["Address"].split(", ")[0]
        city = poi["Address"].split(",")[-1].strip()
        if city.startswith("."):
            city = city[1:]
        city_check = ["Park", "Street", "Shop", "Spa", "Sq."]
        for elem in city_check:
            if elem in city:
                street_address += ", " + city
                city = "<MISSING>"
        state = "<MISSING>"
        zip_code = poi["PostCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["Country"]
        store_number = poi["ID"]
        phone = poi["Telephone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["Latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["Longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = poi["OpeningTimes"]
        hours_of_operation = hours_of_operation if hours_of_operation else "<MISSING>"

        if "Centre" in city:
            street_address += ", " + " ".join(city.split()[:-1])
            city = city.split()[-1]
        if "Ctr." in city:
            street_address += ", " + ".".join(city.split(".")[:-1])
            city = city.split(".")[-1].strip()
        if "Ctr." in street_address:
            city = city.split(".")[-1].strip()
            street_address = street_address.split(" ")[-1]

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
