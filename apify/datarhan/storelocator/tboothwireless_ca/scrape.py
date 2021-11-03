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

    start_url = "https://www.tboothwireless.ca/en/locations/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = []
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_cities = dom.xpath('//div[@id="city-list"]//a/@href')
    for url in all_cities:
        if "#" in url:
            continue
        city_url = urljoin(start_url, url)
        city_response = session.get(city_url)
        city_dom = etree.HTML(city_response.text)
        data = city_dom.xpath('//script[contains(text(), "page.locations =")]/text()')[
            0
        ]
        data = re.findall("page.locations =(.+);", data)[0]
        all_locations += json.loads(data)

    for poi in all_locations:
        location_name = poi["Name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["Address"]
        if poi["Address2"]:
            street_address += " " + poi["Address2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["City"]
        city = city if city else "<MISSING>"
        state = poi["ProvinceAbbrev"]
        state = state if state else "<MISSING>"
        zip_code = poi["PostalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["CountryCode"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = str(poi["LocationId"])
        url_part = location_name.lower().replace(" ", "-")
        store_url = (
            f"https://www.tboothwireless.ca/en/locations/{store_number}/{url_part}/"
        )
        phone = poi["Phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["Google_Latitude"]
        longitude = poi["Google_Longitude"]
        hoo = []
        for elem in poi["HoursOfOperation"]:
            day = elem["DayOfWeek"]
            opens = str(float(elem["Open"]) // 100.00).replace(".", ":") + "0"
            closes = str(float(elem["Close"]) // 100.00).replace(".", ":") + "0"
            hoo.append(f"{day} {opens} - {closes}")
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
