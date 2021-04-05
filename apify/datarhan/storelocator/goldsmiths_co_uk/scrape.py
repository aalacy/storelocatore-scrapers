import re
import csv
import demjson
from urllib.parse import urljoin
from lxml import etree

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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []
    scraped_urls = []

    DOMAIN = "goldsmiths.co.uk"
    start_url = (
        "https://www.goldsmiths.co.uk/store-finder?q={}+1AS&sort=StoreBV-Goldsmiths"
    )

    response = session.get("https://www.goldsmiths.co.uk/store-finder")
    dom = etree.HTML(response.text)
    geo_data = dom.xpath('//script[contains(text(), "storeList")]/text()')[0]
    geo_data = re.findall("storeList =(.+?);", geo_data.replace("\n", ""))[0]
    geo_data = demjson.decode(geo_data)

    all_locations = []
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.BRITAIN],
        max_radius_miles=200,
        max_search_results=None,
    )
    for code in all_codes:
        response = session.get(start_url.format(code.replace(" ", "+")))
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//div[@class="span2 store-details"]/a/@href')
        next_page = dom.xpath('//a[contains(text(), "See more showrooms")]/@href')
        while next_page and next_page[0] not in scraped_urls:
            response = session.get(urljoin(start_url, next_page[0]))
            scraped_urls.append(next_page[0])
            dom = etree.HTML(response.text)
            all_locations += dom.xpath('//div[@class="span2 store-details"]/a/@href')
            next_page = dom.xpath('//a[contains(text(), "See more showrooms")]/@href')

    for url in list(set(all_locations)):
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="stores-store-h"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_data = loc_dom.xpath('//div[@class="address"]/p/text()')
        street_address = raw_data[0]
        city = raw_data[1]
        state = "<MISSING>"
        zip_code = raw_data[-1]
        country_code = "<MISSING>"
        store_number = loc_response.url.split("/")[-1]
        phone = loc_dom.xpath('//h3[text()="Telephone"]/following-sibling::p/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = [elem for elem in geo_data if elem["storeNumber"] == store_number][0]
        latitude = geo["latitude"]
        longitude = geo["longitude"]
        hoo = loc_dom.xpath('//li[@id="weekday_openings"]//text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
