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
    items = []

    DOMAIN = "parkerskitchen.com"
    start_url = "https://parkerskitchen.com/wp-content/themes/parkers/get-locations.php?origAddress=8120+US-280%2C+Ellabell%2C+GA+31308%2C+%D0%A1%D0%A8%D0%90"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)
    response = session.get(start_url, headers=headers)
    data = json.loads(response.text)

    for poi in data:
        store_url = poi["web"]
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        store_number = poi["id"]
        location_type = "<MISSING>"
        hours_of_operation = loc_dom.xpath(
            '//p[strong[contains(text(), "Business Hours:")]]/text()'
        )
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation[:2] if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )
        location_name = poi["name"].replace("&#8217;", "'")
        street_address = poi["address"]
        if poi["address2"]:
            street_address += ", " + poi["address2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        zip_code = poi["postal"]
        raw_data = (
            loc_dom.xpath('//div[@id="locations-text"]/p[1]/text()')[0]
            .strip()
            .split("\t")
        )
        raw_data = [elem.strip() for elem in raw_data if elem.strip()]
        phone = raw_data[-1].split(": ")[-1]
        country_code = "<MISSING>"
        geo_data = re.findall('daddr=(.+?)"', loc_response.text)[0].split("+")
        latitude = geo_data[0]
        latitude = latitude if latitude else "<MISSING>"
        longitude = geo_data[-1]
        longitude = longitude if longitude else "<MISSING>"

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
