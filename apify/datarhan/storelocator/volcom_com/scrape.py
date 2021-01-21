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
    scraped_items = []

    DOMAIN = "volcom.com"
    start_url = "https://www.volcom.com/pages/store-locator"
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath("//div[@data-stores]/div")

    for poi_html in all_locations:
        store_url = poi_html.xpath(".//a[@data-article-tile-image]/@href")
        store_url = urljoin(start_url, store_url[0]) if store_url else "<MISSING>"
        location_name = " ".join(
            [elem.strip() for elem in poi_html.xpath(".//h3/text()")]
        )
        raw_address = poi_html.xpath(".//div[@data-article-tile-excerpt]/p[1]/text()")[
            0
        ].split(", ")
        if len(raw_address) < 3:
            continue
        street_address = raw_address[0]
        city = raw_address[1]
        state = raw_address[2].split()[0]
        zip_code = raw_address[2].split()[-1]
        country_code = raw_address[-1]
        if country_code != "United States":
            continue
        store_number = "<MISSING>"
        phone = poi_html.xpath(".//div[@data-article-tile-excerpt]/p[2]/text()")
        phone = phone[0].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = poi_html.xpath(
            ".//div[@data-article-tile-excerpt]/p[3]/text()"
        )
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

        if len(city.split()[0]) == 2:
            state = city.split()[0]
            zip_code = city.split()[-1]
            city = " ".join(street_address.split("#")[-1].split()[1:])
            zip_code == "<MISSING>"
        if "Coming Soon" in phone:
            phone = "<MISSING>"
            location_type = "Coming Soon"
        if len(zip_code.strip()) == 2:
            zip_code = "<MISSING>"

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
