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
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "westamerica.com"
    start_url = "https://www.westamerica.com/about/locations/"
    response = session.post(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="thrv_wrapper thrv_text_element"]')
    for city_html in all_locations:
        sub_locs_names = city_html.xpath(".//h2/text()")
        for i, location_name in enumerate(sub_locs_names):
            store_url = "<MISSING>"
            street_address = city_html.xpath(".//p[%d]/a/text()" % (i + 1))
            if not street_address:
                street_address = city_html.xpath(".//p[%d]/a/text()" % (i + 2))
            street_address = street_address[0] if street_address else "<MISSING>"
            city = location_name
            city = city if city else "<MISSING>"
            state = "CA"
            zip_code = "<MISSING>"
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            phone = city_html.xpath(".//p[%d]/a/text()" % (i + 1))
            if not phone:
                phone = city_html.xpath(".//p[%d]/a/text()" % (i + 2))
            phone = phone[-1].split(",")[-1] if phone else "<MISSING>"
            location_type = "<MISSING>"
            if "ATM" in phone:
                location_type = "ATM"
                phone = "<MISSING>"
            latitude = city_html.xpath(
                './/h2[%d]/following-sibling::p/a[contains(@href, "sll")]/@href'
                % (i + 1)
            )
            if not latitude:
                latitude = city_html.xpath(
                    './/h2[%d]/following-sibling::p/a[contains(@href, "sll")]/@href'
                    % (i + 2)
                )
            if latitude:
                latitude = re.findall("sll=(.+)&sspn", latitude[0])[0].split(",")[0]
                longitude = city_html.xpath(
                    './/h2[%d]/following-sibling::p/a[contains(@href, "sll")]/@href'
                    % (i + 1)
                )
                if not longitude:
                    longitude = city_html.xpath(
                        './/h2[%d]/following-sibling::p/a[contains(@href, "sll")]/@href'
                        % (i + 2)
                    )
                longitude = re.findall("sll=(.+)&sspn", longitude[0])[0].split(",")[-1]
            else:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            hours_of_operation = city_html.xpath("./p[2]/text()")[1:]
            hours_of_operation = (
                " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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
            if location_name not in scraped_items:
                scraped_items.append(location_name)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
