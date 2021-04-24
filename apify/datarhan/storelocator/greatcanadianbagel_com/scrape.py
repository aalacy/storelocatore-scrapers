import re
import csv
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

    start_url = "http://greatcanadianbagel.com/store-locations/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//table[@class="data"]/tbody/tr')[1:]
    for poi_html in all_locations:
        store_url = start_url
        location_name = "<MISSING>"
        street_address = poi_html.xpath("./td[2]/text()")
        street_address = [e.strip() for e in street_address if e.strip()]
        street_address = " ".join(street_address) if street_address else "<MISSING>"
        if "Eglinton Subway" in street_address:
            street_address += " 2200 Yonge Street Subway Level Suite FC08"
        city = poi_html.xpath(".//*/strong/text()")
        city = city[0].split(", ")[0]
        state = poi_html.xpath(".//*/strong/text()")[0].split(", ")[-1]
        zip_code = "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath(".//td/text()")[-1]
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if poi_html.xpath('.//a[contains(@href, "maps")]/@href'):
            geo = (
                poi_html.xpath('.//a[contains(@href, "maps")]/@href')[0]
                .split("/@")[-1]
                .split(",")[:2]
            )
            if len(geo) == 2:
                if "http" not in geo[0]:
                    latitude = geo[0]
                    longitude = geo[1]
        hours_of_operation = "<MISSING>"
        if "First Canadian Place" in street_address:
            geo = (
                poi_html.xpath('.//a[contains(@href, "maps")]/@href')[0]
                .split("sll=")[-1]
                .split("&")[0]
                .split(",")
            )
            latitude = geo[0]
            longitude = geo[1]

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
