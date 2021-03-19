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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://www.losbalconesperu.com/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@data-mesh-id="SITE_FOOTERinlineContent-gridContainer"]//div[@data-testid="mesh-container-content"]'
    )[:2]
    for poi_html in all_locations:
        store_url = start_url
        raw_data = poi_html.xpath(".//h2//span/text()")
        hoo = []
        if "MONDAY" in raw_data[1]:
            hoo = poi_html.xpath(".//h2//span/text()")[1:7]
            hoo = [e.strip() for e in hoo if e.strip()]
            raw_data = raw_data[:1] + raw_data[7:]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
        location_name = raw_data[0]
        street_address = raw_data[1]
        city = raw_data[2].split(", ")[0].strip()
        state = raw_data[2].split(", ")[-1].split()[0].strip()
        zip_code = raw_data[2].split(", ")[-1].split()[-1].strip()
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = raw_data[-1]
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        item = [
            domain,
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
