import csv
import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl


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
    session = SgRequests()

    items = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    start_url = "https://www.wework.com/locations"
    domain = "wework.com"

    r = session.get(start_url, headers=headers)
    dom = etree.HTML(r.text)
    for country in ["US", "CA"]:
        cities = dom.xpath(
            '//div[@class="markets-list__country markets-list__country--{}"]//a/@href'.format(
                country
            )
        )
        for url in cities:
            city_url = urljoin(start_url, url)
            city_res = session.get(city_url, headers=headers)
            city_dom = etree.HTML(city_res.text)
            locations = city_dom.xpath('//a[contains(@class, "ray-card")]/@href')
            for url in locations:
                store_url = urljoin(start_url, url)
                location_res = session.get(store_url, headers=headers)
                loc_dom = etree.HTML(location_res.text)
                data = loc_dom.xpath('//script[@type="application/ld+json"]/text()')[
                    0
                ].split("/*")[0]
                poi = json.loads(data)
                poi = [e for e in poi["@graph"] if e["@type"] == "LocalBusiness"]
                if not poi:
                    print("Warning!!!", store_url)
                    continue
                poi = poi[0]
                location_name = poi["name"]
                location_name = location_name if location_name else "<MISSING>"
                addr = parse_address_intl(poi["address"]["streetAddress"])
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
                street_address = street_address if street_address else "<MISSING>"
                city = poi["address"]["addressLocality"]
                city = city if city else "<MISSING>"
                state = addr.state
                state = state if state else "<MISSING>"
                zip_code = addr.postcode
                zip_code = zip_code if zip_code else "<MISSING>"
                country_code = addr.postcode
                country_code = country_code if country_code else "<MISSING>"
                store_number = "<MISSING>"
                phone = poi["telephone"]
                phone = phone if phone else "<MISSING>"
                location_type = poi["@type"]
                latitude = poi["geo"]["latitude"]
                longitude = poi["geo"]["longitude"]
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
