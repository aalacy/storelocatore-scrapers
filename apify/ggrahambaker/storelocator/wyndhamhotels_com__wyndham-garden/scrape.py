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

    start_url = "https://www.wyndhamhotels.com/wyndham-garden/locations"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//li[@class="property"]/a/@href')
    for url in all_locations:
        if "overview" not in url:
            continue
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath('//script[contains(text(), "streetAddress")]/text()')
        if poi:
            poi = json.loads(poi[0])
            location_name = poi["name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["address"]["streetAddress"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["address"]["addressLocality"]
            city = city if city else "<MISSING>"
            state = poi["address"].get("addressRegion")
            state = state if state else "<MISSING>"
            zip_code = poi["address"].get("postalCode")
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["address"]["addressCountry"]
            country_code = country_code if country_code else "<MISSING>"
            if country_code not in ["Canada", "United States"]:
                continue
            store_number = "<MISSING>"
            phone = poi["telephone"]
            phone = phone if phone else "<MISSING>"
            location_type = poi["@type"]
            latitude = poi["geo"]["latitude"]
            longitude = poi["geo"]["longitude"]
        else:
            location_name = loc_dom.xpath('//span[@class="prop-name"]/text()')
            location_name = location_name[0] if location_name else "<MISSING>"
            street_address = re.findall(
                "property_city_name = '(.+?)';", loc_response.text
            )
            street_address = street_address[0] if street_address else "<MISSING>"
            city = re.findall("property_city_name = '(.+?)';", loc_response.text)
            city = city[0] if city else "<MISSING>"
            state = re.findall("property_state_code = '(.+?)';", loc_response.text)
            state = state[0] if state else "<MISSING>"
            zip_code = re.findall("property_postal_code = '(.+?)';", loc_response.text)
            zip_code = zip_code[0] if zip_code else "<MISSING>"
            country_code = re.findall(
                "property_country_code = '(.+?)';", loc_response.text
            )
            country_code = country_code[0] if country_code else "<MISSING>"
            store_number = "<MISSING>"
            phone = [
                e
                for e in loc_dom.xpath(
                    '//nav[@id="mainNav"]//a[contains(@href, "tel")]/text()'
                )
                if "(" in e
            ]
            phone = phone if phone else "<MISSING>"
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
