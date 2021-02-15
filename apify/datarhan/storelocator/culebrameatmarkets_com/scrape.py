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

    DOMAIN = "culebrameatmarkets.com"
    start_url = "https://www.culebrameatmarkets.com/home.html"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="paragraph"]')[1:]
    for poi_html in all_locations:
        store_url = "<MISSING>"
        raw_data = poi_html.xpath(".//text()")
        raw_data = [
            elem.strip().replace("\u200b", "") for elem in raw_data if elem.strip()
        ]
        if len(raw_data) == 4:
            raw_data = [" ".join(raw_data[:2])] + raw_data[2:]
        if "San Antonio" in raw_data[0]:
            raw_data = [raw_data[0].split(" San")[0]] + [
                "San" + raw_data[0].split(" San")[-1] + " " + raw_data[1],
                raw_data[-1],
            ]
        location_name = "<MISSING>"
        street_address = raw_data[0]
        city = raw_data[1].split(",")[0].strip()
        state = raw_data[1].split(",")[-1].split()[0].strip()
        zip_code = raw_data[1].split(",")[-1].split()[-1].strip()
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = raw_data[-1]
        phone = phone.strip() if phone and "," not in phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = poi_html.xpath(".//preceding-sibling::div/iframe/@src")[0]
        latitude = re.findall("long=(.+?)&", geo)[0]
        longitude = re.findall("lat=(.+?)&", geo)[0]
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
