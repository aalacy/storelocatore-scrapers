import csv
from lxml import etree
from urllib.parse import urljoin

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

    DOMAIN = "cbsi.net"
    start_url = "https://cbsi.net/Contact.do"

    response = session.post(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@class="gw-contact-yards flex xl6 md6 sm12 xs12"]/div[@class="layout row wrap"]'
    )
    for poi_html in all_locations:
        url = poi_html.xpath(".//a/@href")[0]
        store_url = urljoin(start_url, url)
        location_name = poi_html.xpath(".//h4/a/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_data = poi_html.xpath('.//div[@class="flex xl6 lg6 md6 sm6 xs12"]/p/text()')
        raw_data = [elem.strip() for elem in raw_data]
        street_address = raw_data[0]
        city = raw_data[1].split(", ")[0]
        state = raw_data[1].split(", ")[-1].split()[0]
        zip_code = raw_data[1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = raw_data[2].split(": ")[-1]
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = [
            elem.replace("Hours: ", "") for elem in raw_data if "hours" in elem.lower()
        ]
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
