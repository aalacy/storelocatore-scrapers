import re
import csv
import json
from lxml import etree
from urllib.parse import urljoin

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

    start_url = "https://www.r2o.com/api/stores"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")

    response = session.get("https://www.r2o.com/store-finder")
    token = response.cookies["XSRF-TOKEN"]
    session_id = response.cookies["rent_2_own_session"]

    hdr = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "Cookie": f"XSRF-TOKEN={token}; rent_2_own_session={session_id}",
        "X-Requested-With": "XMLHttpRequest",
    }
    response = session.get(start_url, headers=hdr)
    all_locations = json.loads(response.text)

    for poi in all_locations:
        store_url = urljoin("https://www.r2o.com/", poi["StorePageURL"])
        loc_response = session.get("https://www.r2o.com/heath-ohio")
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi["StoreName"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["Address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["City"]
        city = city if city else "<MISSING>"
        state = poi["State"]
        state = state if state else "<MISSING>"
        zip_code = poi["Zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["Store_ID"]
        phone = poi["Phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["Lat"]
        longitude = poi["Long"]
        hoo = loc_dom.xpath('//div[@class="store-hours"]//text()')
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
