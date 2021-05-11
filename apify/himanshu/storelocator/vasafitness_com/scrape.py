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

    start_url = "https://vasafitness.com/locations/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = []
    all_states = dom.xpath('//div[@class="list-item"]/a/@href')
    for state_url in all_states:
        response = session.get(state_url)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//a[contains(text(), "View Location")]/@href')

    for store_url in all_locations:
        print(store_url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath('//script[contains(text(), "streetAddress")]/text()')

        location_name = loc_dom.xpath('//h1[@class="text-uppercase"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        latitude = loc_dom.xpath("//@data-latt")[0]
        longitude = loc_dom.xpath("//@data-lngg")[0]
        hoo = loc_dom.xpath('//div[@class="hours"]//text()')
        if not hoo:
            continue
        hours_of_operation = " ".join(hoo)
        if poi:
            poi = json.loads(poi[0].split("<script")[0])
            street_address = poi["address"]["streetAddress"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["address"]["addressLocality"]
            city = city if city else "<MISSING>"
            state = poi["address"]["addressRegion"]
            state = state if state else "<MISSING>"
            zip_code = poi["address"]["postalCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["address"]["addressCountry"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = "<MISSING>"
            phone = poi["contactPoint"]["telephone"]
            phone = phone if phone else "<MISSING>"
            location_type = poi["@type"]
        else:
            raw_address = (
                loc_dom.xpath('//div[@class="loc-address"]/text()')[0]
                .strip()
                .split(", ")
            )
            street_address = raw_address[0]
            city = raw_address[1]
            state = raw_address[-1].split()[0]
            zip_code = raw_address[-1].split()[-1]
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
            phone = phone[-1].strip() if phone else "<MISSING>"
            location_type = "<MISSING>"

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
