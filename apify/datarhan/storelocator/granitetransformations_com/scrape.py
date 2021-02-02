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

    DOMAIN = "granitetransformations.com"
    start_url = "https://www.granitetransformations.com/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="row locationContent"]/address')

    for poi_html in all_locations:
        store_url = poi_html.xpath(".//h4/a/@href")
        store_url = store_url[0] if store_url else "<MISSING>"
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi_html.xpath(".//h4/a/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi_html.xpath(".//@data-address")[0]
        if "Call or email" in street_address:
            street_address = "<MISSING>"
        location_type = "<MISSING>"
        city = poi_html.xpath(".//@data-city")[0]
        state = poi_html.xpath(".//@data-state")[0]
        zip_code = poi_html.xpath(".//@data-zip")[0]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath(".//@data-phone")
        phone = phone[0] if phone else "<MISSING>"
        latitude = poi_html.xpath(".//@data-lat")[0]
        longitude = poi_html.xpath(".//@data-lng")[0]
        hours_of_operation = loc_dom.xpath('//div[@class="hours"]//text()')
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation[1:]) if hours_of_operation else "<MISSING>"
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
