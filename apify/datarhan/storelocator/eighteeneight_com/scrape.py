import csv
import json
from lxml import etree

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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

    DOMAIN = "eighteeneight.com"
    start_url = "https://eighteeneight.com/wp-admin/admin-ajax.php?action=store_search&lat=33.68457&lng=-117.8265&max_results=50&search_radius=150&autoload=1"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data:
        store_url = poi["url"]
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["store"].replace("&#8211; ", "")
        street_address = poi["address"]
        if poi["address2"]:
            street_address += ", " + poi["address2"]
        city = poi["city"]
        city = city.split(",")[0] if city else "<MISSING>"
        state = poi["state"]
        if not state:
            state = store_url.split("-")[-1].capitalize()
        state = state if state else "<MISSING>"
        zip_code = poi["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["country"]
        store_number = poi["id"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["lng"]
        longitude = longitude if longitude else "<MISSING>"
        hoo = ""
        if poi["hours"]:
            hoo = etree.HTML(poi["hours"])
            hoo = [elem.strip() for elem in hoo.xpath("//text()")]
        else:
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)
            hoo = loc_dom.xpath(
                '//h3[contains(text(), "HOURS:")]/following-sibling::p/text()'
            )
            hoo = [elem.strip() for elem in hoo]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
