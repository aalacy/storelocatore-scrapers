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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    DOMAIN = "pappadeaux.com"
    start_url = "https://pappadeaux.com/locations/xml_site.php"

    response = session.get(start_url)
    dom = etree.XML(response.text)

    all_locations = dom.xpath("//marker")
    for poi_html in all_locations:
        store_url = poi_html.xpath("@locId")[0]
        store_url = "https://pappadeaux.com/location/" + store_url
        location_name = poi_html.xpath("@name")
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath("@address")[0].split(", ")
        if len(raw_address) == 4:
            raw_address = [", ".join(raw_address[:2])] + raw_address[2:]
        street_address = raw_address[0]
        city = raw_address[1]
        state = raw_address[-1].split()[0]
        zip_code = raw_address[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = poi_html.xpath("@locId")[0]
        phone = poi_html.xpath("@phone")
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi_html.xpath("@lat")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = poi_html.xpath("@lng")
        longitude = longitude[0] if longitude else "<MISSING>"
        hoo_html = etree.HTML(poi_html.xpath("@hoursStatus")[0])
        hours_of_operation = hoo_html.xpath('//div[@class="profile_hours_all"]//text()')
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
