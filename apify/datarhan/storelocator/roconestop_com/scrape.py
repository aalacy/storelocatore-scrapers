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

    DOMAIN = "roconestop.com"
    start_url = "http://roconestop.com/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//strong[contains(text(), "ROC")]')
    for poi_html in all_locations:
        store_url = "http://roconestop.com/locations/"
        location_name = poi_html.xpath("text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_data = poi_html.xpath(".//following::text()")[:4]
        raw_data = [e.strip() for e in raw_data if e.strip()]
        if "Stuckey" in raw_data[0]:
            raw_data = raw_data[1:]
        street_address = raw_data[0]
        city = raw_data[1].split(", ")[0]
        state = raw_data[1].split(", ")[-1].split()[0]
        zip_code = raw_data[1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = location_name.split("#")[-1].strip()
        phone = [e.split(":")[-1] for e in raw_data if ":" in e]
        phone = phone[0].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"

        if state == "ROC":
            city = "<MISSING>"
            state = "<MISSING>"
            zip_code = "<MISSING>"
            phone = "<MISSING>"

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
