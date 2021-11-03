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

    DOMAIN = "pappas.com"
    start_url = "https://pappas.com/locations-list/?msg=none"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="locListLoc"]')

    for poi_html in all_locations:
        store_url = poi_html.xpath(".//a/@href")[0]
        location_name = poi_html.xpath(".//a/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath("text()")
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        street_address = raw_address[0]
        city = raw_address[1].split(", ")[0]
        state = raw_address[1].split(", ")[-1]
        zip_code = "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = raw_address[-1]
        phone = phone if phone else "<MISSING>"
        location_type = store_url.split("/")[2]
        latitude = "<MISSING>"
        longitude = "<MISSING>"
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
