import csv
import yaml
from lxml import etree
from urllib.parse import urljoin
from w3lib.url import add_or_replace_parameter

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

    DOMAIN = "slh.com"
    start_urls = [
        "https://slh.com/api/slh/hotelsearchresults/gethotelsearchresults?adults=2&children=0&sort=ascName&pageIndex=0&resultsPerPage=10&viewType=list&regions=United%20Kingdom",
        "https://slh.com/api/slh/hotelsearchresults/gethotelsearchresults?adults=2&children=0&sort=ascName&pageIndex=0&resultsPerPage=10&viewType=list&country=United%20States",
        "https://slh.com/api/slh/hotelsearchresults/gethotelsearchresults?adults=2&children=0&sort=ascName&pageIndex=0&resultsPerPage=10&viewType=list&country=Canada",
    ]

    all_locations = []
    for url in start_urls:
        response = session.get(url)
        data = yaml.load(response.text)
        all_locations += data["items"]
        for i in range(1, data["totalPages"]):
            page_url = add_or_replace_parameter(url, "pageIndex", str(i))
            response = session.get(page_url)
            data = yaml.load(response.text)
            all_locations += data["items"]

    for poi in all_locations:
        store_url = urljoin(url, poi["detailUrl"])
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi["title"]
        location_name = location_name if location_name else "<MISSING>"
        raw_address = loc_dom.xpath(
            '//div[@class="sc-hotel-location-strained"]/p/text()'
        )[1:]
        addr = parse_address_intl(" ".join(raw_address))
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        street_address = street_address if street_address else "<MISSING>"
        city = poi["location"]["name"].split(", ")[0].strip()
        if street_address.endswith(city):
            street_address = street_address.replace(city, "")
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        if not zip_code:
            zip_code = [e for e in raw_address if len(e.split()[-1]) == 3][0]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["location"]["name"].split(", ")[-1]
        store_number = poi["id"]
        phone = loc_dom.xpath('//a[contains(@class, "telephone-number")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["location"]["coordinates"]["lat"]
        longitude = poi["location"]["coordinates"]["lng"]
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
