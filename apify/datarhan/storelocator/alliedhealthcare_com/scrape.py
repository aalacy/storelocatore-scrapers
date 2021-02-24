import csv
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl


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
    session = SgRequests().requests_retry_session(retries=3, backoff_factor=0.3)

    items = []

    DOMAIN = "alliedhealthcare.com"
    start_url = "https://www.alliedhealthcare.com/wp-content/themes/allied_healthcare/_map/branches.php?lat=52.806693&lng=-2.12066&radius=1000"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath("//marker")

    for poi_html in all_locations:
        store_url = poi_html.xpath("@url")[0]
        store_url = store_url if store_url.strip() else "<MISSING>"
        location_name = poi_html.xpath("@name")
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath("@address")[0]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address = "{} {}".format(
                addr.street_address_2, addr.street_address_1
            )
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi_html.xpath("@branch")
        store_number = (
            store_number[0] if store_number and store_number[0].strip() else "<MISSING>"
        )
        location_type = "<MISSING>"
        phone = poi_html.xpath("@tel")
        phone = phone[0] if phone else "<MISSING>"
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
