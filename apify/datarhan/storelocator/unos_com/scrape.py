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
    scraped_items = []

    DOMAIN = "unos.com"
    start_url = "https://www.unos.com/select-restaurant.php"
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    for poi_html in dom.xpath('//div[@class="location-info"]'):
        store_url = "<MISSING>"
        location_name = poi_html.xpath('.//span[@class="location-name"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath('.//div[@class="location-address"]/text()')
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        if len(raw_address) == 3:
            raw_address = [", ".join(raw_address[:2])] + raw_address[2:]
        city = raw_address[1].split(", ")[0]
        street_address = raw_address[0]
        state = raw_address[1].split(", ")[1].split()[0]
        zip_code = raw_address[1].split(", ")[1].split()[-1]
        country_code = "<MISSING>"
        location_type = "<MISSING>"
        if poi_html.xpath(".//a/@onclick"):
            store_number = poi_html.xpath(".//a/@onclick")[0].split("'")[-2]
        phone = poi_html.xpath('.//span[@class="location-phone"]/text()')[0]
        location_type = "<MISSING>"
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

        check = f"{street_address} {location_name}"
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
