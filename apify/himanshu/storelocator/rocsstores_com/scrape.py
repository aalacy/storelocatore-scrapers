import re
import csv
from lxml import etree
import urllib.parse as urlparse
from urllib.parse import parse_qs

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

    start_url = "https://www.rocsstores.com/locations/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="et_pb_text_inner"]/table/tbody/tr')
    for poi_html in all_locations[1:]:
        if not poi_html.xpath("./td/text()"):
            continue
        store_url = poi_html.xpath('.//a[contains(text(), "Visit")]/@href')
        store_url = store_url[0] if store_url else "<MISSING>"
        location_name = "<MISSING>"
        street_address = poi_html.xpath("./td/text()")[-1].split()[:-1]
        street_address = " ".join(street_address) if street_address else "<MISSING>"
        if store_url != "<MISSING>":
            street_address = poi_html.xpath("./td/text()")[-1]
        city = poi_html.xpath("./td/text()")
        city = city[0] if city else "<MISSING>"
        adr_url = poi_html.xpath('.//a[contains(@href, "mapquest")]/@href')[0]
        parsed_url = urlparse.urlparse(adr_url)
        state = parse_qs(parsed_url.query).get("state")
        state = state[0] if state else "<MISSING>"
        zip_code = parse_qs(parsed_url.query).get("zipcode")
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = parse_qs(parsed_url.query).get("country")
        country_code = country_code[0] if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath("./td/text()")[-1].split()[-1]
        location_type = "<MISSING>"
        latitude = parse_qs(parsed_url.query).get("latitude")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = parse_qs(parsed_url.query).get("longitude")
        longitude = longitude[0] if longitude else "<MISSING>"
        hoo = poi_html.xpath('.//img[@alt="Open 24 Hours"]/@alt')
        hours_of_operation = hoo[0] if hoo else "<MISSING>"

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
