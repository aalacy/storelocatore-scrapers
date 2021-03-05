import re
import csv
from lxml import etree

from sgrequests import SgRequests

DOMAIN = "thelittlegym.com"


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

    session = SgRequests()

    DOMAIN = "tommybahama.com"
    start_url = "https://www.tommybahama.com/en/store-finder?q=&searchStores=true&searchRestaurants=false&searchOutlets=false&searchInternational=true&CSRFToken=b6ba6d9c-9bc3-48f3-952d-2f59a53a4656"
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@id="store-search-results-state"]//a/@href')
    next_page = dom.xpath('//a[contains(text(), "Next")]/@href')
    while next_page:
        page_url = "https://www.tommybahama.com" + next_page[0]
        page_response = session.get(page_url)
        page_dom = etree.HTML(page_response.text)
        all_locations += page_dom.xpath(
            '//div[@id="store-search-results-state"]//a/@href'
        )
        next_page = page_dom.xpath('//a[contains(text(), "Next")]/@href')

    for url in list(set(all_locations)):
        if "restaurants" in url:
            continue
        if "?" in url:
            continue
        if "#" in url:
            continue
        store_url = "https://www.tommybahama.com" + url
        store_response = session.get(store_url)
        store_dom = etree.HTML(store_response.text)
        if not store_dom.xpath(
            '//script[contains(text(), "storeaddressline1")]/text()'
        ):
            continue

        raw_data = (
            store_dom.xpath('//script[contains(text(), "storeaddressline1")]/text()')[0]
            .replace("\n", "")
            .replace("\t", "")
        )
        location_name = store_dom.xpath('//div[@class="store-locator-header"]/text()')
        location_name = (
            location_name[0].strip() if location_name[0].strip() else "<MISSING>"
        )
        street_address = re.findall("storeaddressline1 = '(.+?)';", raw_data)
        street_address = street_address[0] if street_address else "<MISSING>"
        if ";var" in street_address:
            street_address = re.findall("storeaddressline2 = '(.+?)';", raw_data)[0]
        city = re.findall("storeaddresstown = '(.+?)';", raw_data)
        city = city[0] if city else "<MISSING>"
        state = store_dom.xpath(
            '//div[contains(text(), "Address")]/following-sibling::div/text()'
        )
        state = (
            state[-1].strip().split(",")[-1].strip().split()[0]
            if state
            else "<MISSING>"
        )
        zip_code = re.findall("storeaddresspostalCode = '(.+?)';", raw_data)
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = re.findall("storeaddresscountryname = '(.+?)';", raw_data)
        country_code = country_code[0] if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = store_dom.xpath(
            '//div[contains(text(), "Phone #")]/following-sibling::div/text()'
        )
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = re.findall("storelatitude = '(.+?)';", raw_data)
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = re.findall("storelongitude = '(.+?)';", raw_data)
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = store_dom.xpath(
            '//div[contains(text(), "Store Hours")]/following-sibling::div/text()'
        )
        hours_of_operation = (
            hours_of_operation[0].split(":")[-1].strip() if hours_of_operation else ""
        )
        hours_of_operation = (
            hours_of_operation.split(".")[0] if hours_of_operation else "<MISSING>"
        )
        if "For the health" in hours_of_operation:
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
