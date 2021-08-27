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

    DOMAIN = "proimagesports.com"
    start_url = "https://franchise.proimagesports.com/stores/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
    }

    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[contains(@class, "store_list")]/fieldset[legend]')
    for poi_html in all_locations:
        store_url = start_url
        location_name = poi_html.xpath(".//legend/text()")[0]
        raw_address = poi_html.xpath(".//p/text()")
        street_address = raw_address[0]
        city = raw_address[1].split(", ")[0]
        state = " ".join(raw_address[1].split(", ")[-1].split()[:-1])
        zip_code = raw_address[1].split(", ")[-1].split()[-1]
        if not state:
            state = zip_code
            zip_code = "<MISSING>"
        country_code = raw_address[-1]
        if city in country_code:
            country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = "<MISSING>"
        location_type = "<MISSING>"
        geo = poi_html.xpath(".//a/@href")[0]
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if "/maps/place/" in geo and "/@" in geo:
            geo = geo.split("/@")[-1].split(",")[:2]
            latitude = geo[0]
            longitude = geo[1]
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
