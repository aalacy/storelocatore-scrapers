import re
import csv
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
    session = SgRequests()

    items = []

    DOMAIN = "riverisland.com"
    start_url = "https://www.riverisland.com/river-island-stores"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//a[contains(@class, "store-result__title")]/@href')

    for store_url in all_locations:
        loc_response = session.get(store_url)
        if loc_response.status_code != 200:
            continue
        store_number = re.findall('storeId = "(.+)?";', loc_response.text)[0]
        poi = session.get(
            f"https://www.riverisland.com/api/stores/{store_number}"
        ).json()
        poi = poi["data"]

        location_name = poi["storeDisplayName"]
        street_address = poi["address"]["line1"]
        if poi["address"]["line2"]:
            street_address += ", " + poi["address"]["line2"]
        if poi["address"]["line3"]:
            street_address += ", " + poi["address"]["line3"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["city"]
        city = city if city else "<MISSING>"
        state = poi["address"]["stateCode"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["countryCode"]
        phone = poi["telephone"]
        phone = phone if phone.strip() else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["location"]["latitude"]
        longitude = poi["location"]["longitude"]
        hoo = etree.HTML(poi["storeOpeningHoursHtml"]).xpath("//text()")
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
