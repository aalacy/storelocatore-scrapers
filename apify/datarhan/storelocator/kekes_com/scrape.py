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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    DOMAIN = "kekes.com"
    start_url = "https://www.kekes.com/all-locations"

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
    }
    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="sqs-block-content"]/p/a/@href')

    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url, headers=headers)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath("//div/@data-block-json")
        if not poi:
            continue
        poi = json.loads(poi[0])

        raw_address = loc_dom.xpath('//div[@class="sqs-block-content"]/p[2]/a/text()')
        if not raw_address:
            raw_address = loc_dom.xpath(
                '//div[@class="sqs-block-content"]/p[3]/a/text()'
            )
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        if len(raw_address) != 2:
            raw_address = [" ".join(raw_address[:2])] + raw_address[2:]
        location_name = loc_dom.xpath('//div[@class="sqs-block-content"]/h1/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = raw_address[0]
        city = raw_address[-1].split(", ")[0]
        state = raw_address[-1].split(", ")[-1].split()[0]
        zip_code = raw_address[-1].split(", ")[-1].split()[-1]
        country_code = poi["location"]["addressCountry"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["location"]["mapZoom"]
        store_number = store_number if store_number else "<MISSING>"
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        if phone == "<MISSING>":
            phone = loc_dom.xpath('//div[@class="sqs-block-content"]/p[1]/text()')[0]
        if "NOW OPEN" in phone:
            phone = loc_dom.xpath('//div[@class="sqs-block-content"]/p[2]/text()')[0]
        location_type = "<MISSING>"
        if "COMING SOON" in phone:
            phone = "<MISSING>"
            location_type = "COMING SOON"
        latitude = poi["location"]["mapLat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["location"]["mapLng"]
        longitude = longitude if longitude else "<MISSING>"
        hoo = loc_dom.xpath('//p[contains(text(), "open daily")]/text()')[0]
        hours_of_operation = re.findall(r"locations are (.+)\(", hoo)[0]

        if "FL" in city:
            state = city.split(",")[-1].split()[0]
            city = city.split(",")[0]

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
