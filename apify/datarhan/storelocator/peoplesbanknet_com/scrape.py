import re
import csv
import json
from lxml import etree
from w3lib.url import add_or_replace_parameter

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

    start_url = "https://www.peoplesbanknet.com/wp-json/wpcm-locations/v1/view/states?imahuman=16749697&zipcode=&distance=50000&service_type=ALL_SERVICES_TYPES&service_type_text=All%20Service%20Types&page=1"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    all_locations = json.loads(response.text)
    next_page = 2
    while next_page:
        response = session.get(
            add_or_replace_parameter(start_url, "page", str(next_page)), headers=hdr
        )
        if len(json.loads(response.text)) != 0:
            all_locations += json.loads(response.text)
            next_page += 1
        else:
            next_page = None

    for poi in all_locations:
        store_url = poi["url"]
        location_name = poi["title"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address_unformatted"].split("\r\n")[0]
        city = location_name
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["postal_code"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["id"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        if poi["is_atm_only"] == "1":
            location_type = "atm only"
        latitude = poi["lat"]
        longitude = poi["lng"]
        hoo_html = etree.HTML(poi["hours"])
        hoo = hoo_html.xpath("//text()")
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo[1:]) if hoo else "<MISSING>"
        if hours_of_operation == "No Drive-Thru":
            hours_of_operation = "<MISSING>"
            location_type = "temporary closed"
        hours_of_operation = (
            hours_of_operation.replace("No Drive-Thru", "")
            .replace("Transactions", "")
            .strip()
        )

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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
