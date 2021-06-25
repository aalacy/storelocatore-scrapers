import re
import csv
from lxml import etree

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
    # Your scraper here
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []
    scraped_items = []

    start_url = "https://www.assurant.com/office-locations"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[h4[@class="font-primary office-title"]]')
    for poi_html in all_locations:
        store_url = start_url
        location_name = poi_html.xpath(".//h4/strong/text()")[0].strip()
        street_address = poi_html.xpath(
            './/div[@class="office-description-address"]/text()'
        )[0]
        raw_address = poi_html.xpath('.//div[@class="office-description-city"]/text()')[
            0
        ]
        addr = parse_address_intl(raw_address)
        city = poi_html.xpath('.//div[@class="office-description-city"]/text()')[
            0
        ].split(",")[0]
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi_html.xpath(".//parent::div[1]/@class")[0].split("office")[-1]
        if country_code.startswith("-"):
            country_code = country_code[1:]
        if country_code == "Argentina":
            zip_code = poi_html.xpath(
                './/div[@class="office-description-city"]/text()'
            )[0].split()[-1]
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//p[@class="office-description-phone"]/a/text()')
        phone = phone[0].strip() if phone else "<MISSING>"
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
        check = f"{location_name} {street_address}"
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
