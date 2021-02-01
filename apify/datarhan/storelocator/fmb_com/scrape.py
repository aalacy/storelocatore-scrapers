import json
import csv
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

    DOMAIN = "fmb.com"
    start_url = "https://fmb.com/api/sitecore/Maps/GetMapPoints"

    formdata = {"itemId": "{1E8E6B51-E5BA-4D7A-B8A1-38ADEE35E492}"}
    response = session.post(start_url, data=formdata)
    data = json.loads(response.text)

    for poi in data:
        store_url = urljoin(start_url, poi["Url"])
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi["Name"]
        raw_address = poi["Address"].split("\r\n")
        street_address = raw_address[0]
        city = raw_address[-1].split(", ")[0]
        state = raw_address[-1].split(", ")[-1].split()[0]
        zip_code = raw_address[-1].split(", ")[-1].split()[-1]
        latitude = poi["Location"].split(", ")[0]
        longitude = poi["Location"].split(", ")[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//span[@itemprop="telephone"]/text()')
        phone = phone[0].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = loc_dom.xpath('//meta[@itemprop="openingHours"]/@content')
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
