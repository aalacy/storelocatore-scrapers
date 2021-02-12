import re
import csv
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


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
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "hobbycraft.co.uk"
    start_url = "https://www.hobbycraft.co.uk/storesearch?userSearch={}"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36"
    }

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.BRITAIN],
        max_radius_miles=200,
        max_search_results=None,
    )

    all_locations = []
    for code in all_codes:
        response = session.get(start_url.format(code), headers=hdr)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//div[contains(@id, "stores")]')

    for poi_html in all_locations:
        store_url = poi_html.xpath('.//a[contains(text(), "View this store")]/@href')
        store_url = urljoin(start_url, store_url[0])
        location_name = poi_html.xpath(".//h4/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath(".//address//text()")
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        street_address = " ".join(raw_address[:-2])
        city = raw_address[-2]
        state = "<MISSING>"
        zip_code = raw_address[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//div[@class="store-contact-details"]//a/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"

        loc_response = session.get(store_url)
        latitude = re.findall("lat':(.+?),", loc_response.text)
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = re.findall("lng':(.+?),", loc_response.text)
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = "<MISSING>"

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
