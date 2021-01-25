import re
import csv
import yaml
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

    DOMAIN = "californiatortilla.com"
    start_url = "https://www.californiatortilla.com/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "locations = ")]/text()')[0]
    data = re.findall("locations =(.+);", data.replace("\n", ""))
    data = (
        data[0]
        .replace("new google.maps.LatLng(", "")
        .replace("),\t", ",")
        .replace("\t", "")
    )
    data = yaml.load(data)

    for poi in data:
        store_url = poi["url"]
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        raw_address = loc_dom.xpath(
            '//span[contains(text(), "Address")]/following-sibling::p[1]/text()'
        )
        raw_address = [elem.strip() for elem in raw_address]

        location_name = poi["name"].replace("&#8211;", "")
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["street"]
        city = raw_address[1].split(", ")[0]
        state = raw_address[1].split(", ")[-1].split()[0]
        zip_code = poi["zip"]
        country_code = "<MISSING>"
        store_number = poi["id"]
        latitude = poi["coords"].split(",")[0]
        longitude = poi["coords"].split(",")[-1]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = loc_dom.xpath(
            '//span[contains(text(), "Hours")]/following-sibling::p/text()'
        )
        hours_of_operation = (
            " ".join(hours_of_operation).replace("\n", "").replace("\t", "")
            if hours_of_operation
            else "<MISSING>"
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
