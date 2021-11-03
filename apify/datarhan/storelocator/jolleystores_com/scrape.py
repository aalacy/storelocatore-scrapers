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

    DOMAIN = "jolleystores.com"
    start_url = "http://jolleystores.com/locations"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = []
    all_states = dom.xpath(
        '//h3[contains(text(), "Locations")]/following-sibling::ul//li/a/@href'
    )
    for url in all_states:
        response = session.get(url)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//li[contains(@class, "page_item")]/a/@href')

    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        location_name = loc_dom.xpath('//div[@id="BoxBG"]//h3/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath('//div[@id="BoxBG"]//div[@class="right"]/text()')[
            1:3
        ]
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        street_address = raw_address[0]
        city = raw_address[1].split(", ")[0]
        state = raw_address[1].split(", ")[-1].split()[0]
        zip_code = raw_address[1].split(", ")[-1].split()[-1]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = loc_dom.xpath('//div[@id="BoxBG"]//div[@class="right"]/text()')[
            0
        ].split()[0][1:]
        phone = loc_dom.xpath('//div[@id="BoxBG"]//div[@class="right"]/text()')[
            3
        ].strip()
        if "open" in phone.lower():
            phone = loc_dom.xpath('//div[@id="BoxBG"]//div[@class="right"]/text()')[
                4
            ].strip()
        if "sat" in phone.lower():
            phone = loc_dom.xpath('//div[@id="BoxBG"]//div[@class="right"]/text()')[
                5
            ].strip()
        phone = phone.replace("Store", "").strip()
        location_type = "<MISSING>"
        geo = (
            loc_dom.xpath("//iframe/@src")[0].split("ll=")[-1].split("&")[0].split(",")
        )
        if len(geo) == 1:
            geo = (
                loc_dom.xpath("//iframe/@src")[0]
                .split("ll=")[-1]
                .split("&")[0]
                .split(",")[0]
                .split("1d")[-1]
                .split("!3d")[0]
                .split("!2d")
            )
        latitude = geo[0]
        if len(latitude.split(".")[0]) == 4:
            latitude = latitude[2:]
        latitude = latitude if latitude else "<MISSING>"
        longitude = geo[1]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = "<MISSING>"

        if len(city.split()) > 2:
            state = city.split()[-2]
            zip_code = city.split()[-1]
            city = " ".join(city.split()[:-2])

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
