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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []
    scraped_items = []

    DOMAIN = "lindsayandgilmour.co.uk"
    start_url = "https://lindsayandgilmour.co.uk/location/branch-list/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="ct-code-block"]/table/tbody/tr')[1:]
    for poi_html in all_locations:
        raw_data = poi_html.xpath(".//text()")
        raw_data = [elem.strip() for elem in raw_data if elem.strip()]
        if raw_data[0] == "Branch":
            continue

        store_url = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = raw_data[-1]
        if "David Wynne" in hours_of_operation:
            hours_of_operation = "<MISSING>"
        location_name = raw_data[0]
        address_raw = raw_data[1].split(", ")
        street_address = address_raw[0]
        city = address_raw[1]
        state = "<MISSING>"
        zip_code = address_raw[-1].replace("\n", " ")
        country_code = "UK"
        store_number = "<MISSING>"
        phone = raw_data[2]
        latitude = "<MISSING>"
        longitude = "<MISSING>"

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
