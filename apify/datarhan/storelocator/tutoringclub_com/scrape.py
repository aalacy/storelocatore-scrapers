import csv
import json
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

    DOMAIN = "tutoringclub.com"
    start_url = "https://www.tutoringclub.com/wp-admin/admin-ajax.php?action=store_search&lat=37.09024&lng=-95.71289&max_results=25&search_radius=50&autoload=1"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data:
        if poi["country"] != "United States":
            continue
        store_url = poi["url"]
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi["store"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"].replace(",", "")
        state = poi["state"]
        zip_code = poi["zip"]
        country_code = poi["country"]
        store_number = poi["id"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        if loc_dom.xpath('//p[contains(text(), "COMING SOON!")]'):
            location_type = "coming soon"
        latitude = poi["lat"]
        longitude = poi["lng"]
        hours_of_operation = ""
        if poi["hours"]:
            hours_of_operation = etree.HTML(poi["hours"])
            hours_of_operation = hours_of_operation.xpath("//text()")
        if not hours_of_operation:
            hours_of_operation = loc_dom.xpath(
                '//div[@class="single-detail club-open-hours"]//div[@class="the-content"]/p/text()'
            )[:-1]
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
