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

    start_url = "https://www.ritzcarlton.com/en/hotels"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//li[h2[contains(text(), "USA & Canada")]]//a/@href')
    for store_url in all_locations:
        loc_response = session.get(store_url + ".headeronly.html", headers=hdr)
        if loc_response.status_code != 200:
            continue
        print(store_url, loc_response.status_code)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath('//script[contains(text(), "address")]/text()')
        if not poi:
            continue
        poi = json.loads(poi[0].replace('"City by the Bay"', "City by the Bay"))

        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["streetAddress"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["addressLocality"]
        if city.endswith(","):
            city = city[:-1]
        state = poi["address"].get("addressRegion")
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["telephone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["@type"]

        geo_response = session.get(
            store_url + "/hotel-overview/directions", headers=hdr
        )
        if geo_response.status_code != 200:
            continue
        geo_dom = etree.HTML(geo_response.text)
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        geo = (
            geo_dom.xpath("//iframe/@src")[-1]
            .split("1d")[-1]
            .split("!3d")[0]
            .split("!2d")
        )
        if len(geo) == 2:
            latitude = geo[0][2:]
            longitude = geo[1]
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
