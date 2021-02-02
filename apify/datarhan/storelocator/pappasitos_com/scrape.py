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

    DOMAIN = "pappasitos.com"
    start_url = "https://pappasitos.com/locations/xml_site.php"

    response = session.get(start_url)
    dom = etree.XML(response.text)
    all_locations = dom.xpath("//marker")

    for poi_html in all_locations:
        store_url = "https://pappasitos.com/location/{}".format(
            poi_html.xpath("@locId")[0]
        )
        location_name = poi_html.xpath("@name")
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi_html.xpath("@street")
        street_address = street_address[0] if street_address else "<MISSING>"
        city = poi_html.xpath("@city")
        city = city[0].split(", ")[0] if city else "<MISSING>"
        state = poi_html.xpath("@city")
        state = state[0].split(", ")[-1].split()[0]
        zip_code = poi_html.xpath("@city")
        zip_code = zip_code[0].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = poi_html.xpath("@locId")[0]
        phone = poi_html.xpath("@phone")
        phone = phone[0] if phone and phone[0].strip() else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi_html.xpath("@lat")[0]
        longitude = poi_html.xpath("@lng")[0]
        hoo = etree.HTML(poi_html.xpath("@hoursStatus")[0])
        hours_of_operation = hoo.xpath('//div[@class="profile_hours_all"]//text()')
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )
        hoo = hours_of_operation.split("p.m. 11:00 a.m. – 10:00 p.m.")[0] + "p.m."
        hoo = hoo.split("p.m. 10:00 a.m. – 10:00 p.m.")[0] + "p.m."
        hours_of_operation = hoo.split("p.m. 4:00 p.m. – 9:00 p.m")[0] + "p.m."
        hours_of_operation = hours_of_operation.replace("p.m.p.m.p.m.", "p.m.").replace(
            "p.m.p.m.", "p.m."
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
