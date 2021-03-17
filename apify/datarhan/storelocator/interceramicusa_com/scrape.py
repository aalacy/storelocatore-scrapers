import re
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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []
    scraped_items = []

    start_url = "https://interceramicusa.com/wp-admin/admin-ajax.php?action=store_search&lat=32.776664&lng=-96.796988&max_results=25&search_radius=50&autoload=1"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    data = json.loads(response.text)

    for poi in data:
        store_url = "https://interceramicusa.com/dealer-locator/"
        location_name = poi["store"]
        location_name = location_name if location_name else "<MISSING>"
        location_name = (
            location_name.replace("&#038;", "&")
            .replace("\&#8217;", "'")
            .replace("&#8217;", "'")
        )
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state.split("-")[0] if state else "<MISSING>"
        street_address = poi["address"]
        if f"{state}.".lower() in street_address.lower():
            street_address = street_address.split(", ")[0]
        if city.lower() in street_address.lower():
            street_address = street_address.split(", ")[0]
        if city.lower() in street_address.lower():
            street_address = street_address.split(city)[0].strip()
        street_address = (
            street_address.split(", La ")[0] if street_address else "<MISSING>"
        )
        zip_code = poi["zip"]
        zip_code = zip_code.split()[-1] if zip_code else "<MISSING>"
        country_code = poi["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["id"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["display_type"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["lat"]
        latitude = latitude if latitude else "<MISSINg>"
        longitude = poi["lng"]
        longitude = longitude if longitude else "<MISSING>"
        hoo = etree.HTML(poi["hours"])
        hoo = hoo.xpath("//text()")
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        item = [
            domain,
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
        check = f"{location_name} {street_address}"
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
