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
    session = SgRequests()

    items = []

    DOMAIN = "cosstores.com"
    start_urls = [
        "https://www.cosstores.com/ca/en/store-locator/united-states/",
        "https://www.cosstores.com/ca/en/store-locator/united-kingdom/",
        "https://www.cosstores.com/ca/en/store-locator/canada/",
    ]

    for start_url in start_urls:
        response = session.get(start_url)
        dom = etree.HTML(response.text)

        all_locations = dom.xpath('//div[@class="store"]')
        for poi_html in all_locations:
            store_url = "<MISSING>"
            location_name = poi_html.xpath(".//h2/text()")
            location_name = location_name[0] if location_name else "<MISSING>"
            raw_address = poi_html.xpath(".//p/text()")[:4]
            raw_address = " ".join(
                [elem.strip() for elem in raw_address if elem.strip()]
            )
            parsed_adr = parse_address_intl(raw_address)
            street_address = parsed_adr.street_address_1
            city = parsed_adr.city
            city = city if city else "<MISSING>"
            state = parsed_adr.state
            state = state if state else "<MISSING>"
            zip_code = parsed_adr.postcode
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = parsed_adr.country
            country_code = country_code if country_code else "<MISSING>"
            store_number = "<MISSING>"
            phone = poi_html.xpath(".//p/text()")[4].split(": ")[-1]
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours_of_operation = poi_html.xpath(
                './/p[contains(text(), "Opening Hours")]/text()'
            )
            hours_of_operation = (
                " ".join(hours_of_operation[1:]).split("Special")[0]
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
