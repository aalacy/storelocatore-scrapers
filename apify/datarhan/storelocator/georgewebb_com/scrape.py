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

    DOMAIN = "georgewebb.com"
    start_url = "https://georgewebb.com/hwstorelocation/storesearch?lat=43.05328249999999&lng=-88.1584129&radius=5000&units=Miles&cat=All%20Categories"

    response = session.get(start_url)
    dom = etree.XML(response.text)
    all_locations = dom.xpath("//marker")

    for poi_html in all_locations:
        store_url = "<MISSING>"
        location_name = poi_html.xpath("@name")
        location_name = location_name[0] if location_name else "<MISSSING>"
        street_address = poi_html.xpath("@address")[0]
        city = poi_html.xpath("@city")[0]
        state = poi_html.xpath("@state")[0]
        zip_code = poi_html.xpath("@zip")[0]
        country_code = poi_html.xpath("@country")[0]
        store_number = "<MISSING>"
        phone = poi_html.xpath("@phone")[0]
        phone = phone if phone.strip() else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi_html.xpath("@lat")[0]
        longitude = poi_html.xpath("@lng")[0]
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
