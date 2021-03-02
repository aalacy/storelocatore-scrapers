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
    items = []

    session = SgRequests()

    DOMAIN = "yvesrocher.ca"
    start_url = "https://www.yvesrocher.ca/en/all-about-our-stores/stores-and-spa/SL"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath(
        '//li[@class="m-t_S inline-block p-x_default tab_text_size_default width_25p"]/a[contains(@href, "/stores-and-spa/")]/@href'
    )

    for url in all_locations:
        store_url = f"https://www.yvesrocher.ca/en{url}"
        if "spa//" in store_url:
            continue
        loc_response = session.get(store_url)
        poi = re.findall("store = (.+);", loc_response.text)[0]
        poi = json.loads(poi)

        location_name = poi["name"]
        street_address = poi["address1"]
        if poi["address2"]:
            street_address += " " + poi["address2"]
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["region"]
        zip_code = poi["zipCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["countryName"]
        store_number = "<MISSING>"
        phone = poi["phoneNumber"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["location"][1]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["location"][0]
        longitude = longitude if longitude else "<MISSING>"
        hoo = []
        for k, hours in poi.items():
            if "opening" in k:
                day = k.replace("opening", "")
                hoo.append(f"{day} {hours}")
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
