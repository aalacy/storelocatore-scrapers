import re
import csv
import demjson
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

    start_url = "https://www.flyingstarcafe.com/find-us/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)

    all_locations = all_locations = re.findall(
        r"location_data.push\((.+?)\);",
        response.text.replace("\n", "").replace("\t", ""),
    )
    for poi in all_locations:
        poi = demjson.decode(poi)
        store_url = poi["self_url"]
        if store_url in scraped_items:
            continue
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi["name"]
        poi_html = etree.HTML(poi["address"])
        street_address = " ".join(
            poi_html.xpath('.//div[@class="street-address"]/text()')
        ).strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]
        city = poi_html.xpath('.//span[@class="locality"]/text()')[0].strip()
        state = poi_html.xpath('.//span[@class="region"]/text()')[0]
        zip_code = poi_html.xpath('.//span[@class="postal-code"]/text()')[0]
        country_code = poi["country"].split("(")[-1][:-1]
        store_number = "<MISSING>"
        phone = poi["phone"]
        location_type = "<MISSING>"
        latitude = poi["lat"]
        longitude = poi["long"]
        hoo = loc_dom.xpath('//table[@class="wpseo-opening-hours"]//text()')
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
        if store_url not in scraped_items:
            scraped_items.append(store_url)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
