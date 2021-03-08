import re
import csv
import json
from lxml import etree

from sgrequests import SgRequests
from sgselenium import SgFirefox


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf-8") as output_file:
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
    session = SgRequests()

    items = []

    DOMAIN = "aureliospizza.com"
    start_url = "https://www.aureliospizza.com/locations/"

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    }
    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[@id="maplistko-js-extra"]/text()')[0]
    data = re.findall("ParamsKo =(.+);", data)
    data = json.loads(data[0])

    for poi in data["KOObject"][0]["locations"]:
        store_url = poi["locationUrl"]
        with SgFirefox() as driver:
            driver.get(store_url)
            loc_dom = etree.HTML(driver.page_source)
        raw_address = loc_dom.xpath('//div[@class="location"]//a/text()')
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        location_name = poi["title"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = raw_address[0]
        street_address = street_address if street_address else "<MISSING>"
        city = location_name.split(",")[0]
        state = raw_address[0].split(", ")[-1].split()
        if state[-1].isdigit():
            state = state[-2]
        else:
            state = state[-1]
        city = city.split(state)[0].split(" - ")[0]
        street_address = street_address.split(city)[0].split(",")[0].strip()
        zip_code = raw_address[0].split(", ")[-1].split()[-1]
        phone = raw_address[-1]
        country_code = "<MISSING>"
        store_number = loc_dom.xpath("//article/@id")[0].split("-")[-1]
        location_type = "<MISSING>"
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        hours_of_operation = loc_dom.xpath(
            '//h5[contains(text(), "Hours")]/following-sibling::p[1]/text()'
        )
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
