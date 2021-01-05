import csv
from lxml import etree

from sgselenium import SgFirefox


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
    items = []

    DOMAIN = "salsaritas.com"
    start_url = "https://salsaritas.com/locations/"

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)
    all_locations = dom.xpath('//div[@class="wpgmp_locations"]')

    for poi_html in all_locations:
        store_url = poi_html.xpath('.//div[@class="wpgmp_location_title_2"]/a/@href')
        store_url = (
            "https://salsaritas.com" + store_url[0] if store_url else "<MISSING>"
        )
        location_name = poi_html.xpath('.//div[@class="wpgmp_location_title"]/a/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        if poi_html.xpath('.//div[@class="wpgmp_locations_list_map"]/a/@href'):
            raw_address = poi_html.xpath(
                './/div[@class="wpgmp_locations_address"]/text()'
            )[0].split(", ")
            if len(raw_address) < 3:
                raw_address = (
                    poi_html.xpath('.//div[@class="wpgmp_locations_list_map"]/a/@href')[
                        0
                    ]
                    .split("//")[-1]
                    .split("/@")[0]
                    .replace("+", " ")
                    .split(", ")
                )
        else:
            raw_address = poi_html.xpath('.//a[@class="get-directions "]/@href')[
                0
            ].split(", ")
        for elem in ["Suit", "Court", "%"]:
            if elem in raw_address[1]:
                raw_address = [" ".join(raw_address[:2])] + raw_address[2:]
        street_address = raw_address[0].split("=")[-1].replace("%", " ")
        city = raw_address[1]
        state = raw_address[2].split()[0]
        zip_code = raw_address[2].split()[-1]
        country_code = "<MISSING>"
        store_number = poi_html.xpath('.//div[@class="wpgmp_location_id"]/text()')
        store_number = store_number[0] if store_number else "<MISSING>"
        phone = poi_html.xpath('.//div[@class="wpgmp_locations_phone"]/a/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if poi_html.xpath('.//div[@class="wpgmp_locations_list_map"]/a/@href'):
            geo = (
                poi_html.xpath('.//div[@class="wpgmp_locations_list_map"]/a/@href')[0]
                .split("/@")[-1]
                .split(",")[:2]
            )
            if len(geo) == 2:
                if "https" not in geo[0]:
                    latitude = geo[0]
                    longitude = geo[1]
        hours_of_operation = poi_html.xpath(
            './/div[@class="wpgmp_locations_opening_hours"]/span/text()'
        )
        hours_of_operation = (
            " ".join(hours_of_operation).replace("<", "")
            if hours_of_operation
            else "<MISSING>"
        )

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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
