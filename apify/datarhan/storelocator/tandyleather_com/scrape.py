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
    scraped_items = []

    DOMAIN = "tandyleather.com"
    start_url = "https://cdn.shopify.com/s/files/1/0063/5997/3970/t/44/assets/sca.storelocatordata.json?v=1613368747&formattedAddress=&boundsNorthEast=&boundsSouthWest="

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data:
        store_url = poi["web"]
        location_name = poi["name"]
        street_address = poi["address"]
        if poi.get("address2"):
            street_address += ", " + poi["address2"]
        city = poi["city"]
        state = poi["state"]
        zip_code = poi["postal"]
        country_code = poi["country"]
        store_number = poi["id"]
        location_type = "<MISSING>"
        phone = poi["phone"]
        latitude = poi["lat"]
        longitude = poi["lng"]

        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        hours_of_operation = loc_dom.xpath('//div[@class="loc-hours"]/p/text()')
        hours_of_operation = [elem.strip() for elem in hours_of_operation]
        hours_of_operation = " ".join(hours_of_operation)

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

        check = "{} {}".format(street_address, location_name)
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
