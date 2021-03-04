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

    start_url = "https://www.outrigger.com/hotels-resorts"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@class="promo-cta-content"]/a[@class="promo-cta"]/@href'
    )
    for url in all_locations:
        store_url = urljoin(start_url, url)
        data_url = f"https://schema.milestoneinternet.com/schema/outrigger.com{url}/schema.json"
        d_response = session.get(data_url)
        if d_response.status_code == 200:
            poi = json.loads(d_response.text)

            location_name = poi[2]["name"][0]
            street_address = poi[2]["address"]["streetAddress"]
            street_address = (
                street_address.strip() if street_address.strip() else "<MISSING>"
            )
            city = poi[2]["address"]["addressLocality"]
            state = poi[2]["address"]["addressRegion"]
            zip_code = poi[2]["address"]["postalCode"].strip()
            zip_code = zip_code if zip_code else "<MISSING>"
            if zip_code == "Islands":
                zip_code = "<MISSING>"
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            phone = poi[2]["telephone"]
            phone = phone.strip() if phone else "<MISSING>"
            location_type = poi[2]["@type"]
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours_of_operation = "<MISSING>"
        else:
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)
            raw_address = loc_dom.xpath(
                '//div[@class="col-md-4"]/p/span[@style="font-weight: 500;"]/text()'
            )[:2]
            location_name = loc_dom.xpath('//div[@class="no-image"]/h1/text()')[0]
            street_address = raw_address[0].strip()
            city = raw_address[1].split(",")[0].strip()
            state = raw_address[1].split(",")[-1].split()[0]
            zip_code = raw_address[1].split(",")[-1].split()[-1]
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            phone = loc_dom.xpath(
                '//div[@class="col-md-4"]/p/span[@style="font-weight: 500;"]/a[contains(@href, "tel")]/text()'
            )
            phone = phone[0].strip() if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours_of_operation = "<MISSING>"

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
