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

    DOMAIN = "covance.com"
    start_url = "https://www.covance.com/locations.html"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="locations-results-row"]')

    for poi_html in all_locations[1:]:
        store_url = "<MISSING>"
        location_name = poi_html.xpath('.//li[@class="name"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath('.//li[@class="address"]/text()')
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        if (
            "," not in poi_html.xpath('.//li[@class="title"]/text()')[0]
            and " United Kingdom" not in raw_address[-1]
        ):
            continue
        raw_address = [" ".join(raw_address[:2])] + raw_address[2:]
        country_code = "<MISSING>"
        if "USA" in raw_address[-1]:
            country_code = "USA"
            raw_address = raw_address[:-1] + [" ".join(raw_address[-1].split()[:-1])]
        country_code = (
            "United Kingdom" if "United Kingdom" in raw_address[-1] else "<MISSING>"
        )
        city = poi_html.xpath('.//li[@class="title"]/text()')[0].split(", ")[0]
        city = city if city else "<MISSING>"
        street_address = raw_address[0].replace(city, "")
        state = poi_html.xpath('.//li[@class="title"]/text()')[0].split(", ")[-1]
        state = state if state else "<MISSING>"
        street_address = street_address.split(", {}".format(state))[0]
        zip_code = raw_address[-1].split()[-1]
        if country_code == "United Kingdom":
            zip_code = " ".join(raw_address[-1].split()[-2:])
        zip_code = zip_code if zip_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//li[@class="phone"]/a/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"

        if country_code == "United Kingdom":
            [
                "Osprey House Westacott Way",
                "Littlewick Green",
                "Maidenhead",
                "SL6 3QH, United Kingdom",
            ]
            country_code = "United Kingdom"
            city = raw_address[2]
            street_address = " ".join(raw_address[:2])
            state = "<MISSING>"
            zip_code = raw_address[-1].split(", ")[0]

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

        check = f"{street_address} {city}"
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
