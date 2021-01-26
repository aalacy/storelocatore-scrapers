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

    DOMAIN = "ragstock.com"
    start_url = "https://ragstock.com/stores/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
    }

    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="stores-name"]')

    for poi_html in all_locations:
        store_url = poi_html.xpath(".//following-sibling::div[2]/a/@href")
        store_url = store_url[0] if store_url else "<MISSING>"
        location_name = poi_html.xpath("text()")
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        raw_data = poi_html.xpath(
            './/following-sibling::div[@class="stores-info"][1]/text()'
        )
        raw_data = [elem.strip() for elem in raw_data if elem.strip()]
        if "Space" in raw_data[1]:
            raw_data = [", ".join(raw_data[:2])] + raw_data[2:]
        street_address = raw_data[0]
        city = raw_data[1].split(", ")[0]
        state = raw_data[1].split(", ")[-1].split()[0]
        zip_code = raw_data[1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = raw_data[2].strip()
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = raw_data[-1].strip()

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
