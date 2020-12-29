import re
import csv
import json
from urllib.parse import urljoin
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
    session = SgRequests().requests_retry_session(retries=3, backoff_factor=0.3)

    items = []

    DOMAIN = "daveandbusters.com"
    start_url = "https://www.daveandbusters.com/locations"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="location-list-item"]//a/@href')
    for url in list(set(all_locations)):
        store_url = urljoin(start_url, url)
        response = session.get(store_url, headers=hdr)
        dom = etree.HTML(response.text)
        loc_id = re.findall(r"AddLocationId\((\d+)\);", response.text)
        try:
            response = session.get(
                "https://www.daveandbusters.com/umbraco/api/LocationDataApi/GetLocationDataById?locationId={}".format(
                    loc_id[0]
                ),
                headers=hdr,
            )
        except Exception:
            response = session.get(
                "https://www.daveandbusters.com/umbraco/api/LocationDataApi/GetLocationSpecialDataById?locationId={}".format(
                    loc_id[0]
                ),
                headers=hdr,
            )
        poi = json.loads(response.text)

        location_name = poi["DisplayName"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["Address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["City"]
        city = city if city else "<MISSING>"
        state = poi["State"]
        state = state if state else "<MISSING>"
        zip_code = poi["Zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["Country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["ID"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["Phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["Latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["Longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = poi["Hours"]
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )
        if poi["TempClosed"]:
            hours_of_operation = "<MISSING>"
            location_type = "temporary closed"

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
