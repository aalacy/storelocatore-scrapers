import re
import csv
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
    items = []
    scraped_items = []

    session = SgRequests()

    DOMAIN = "tommybahama.com"
    start_url = "https://www.tommybahama.com/en/store-finder?q=&searchStores=true&searchRestaurants=true&searchOutlets=true&searchInternational=false"
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[@class="store-finder-results-title"]/@href')
    next_page = dom.xpath('//a[contains(text(), "Next")]/@href')
    while next_page:
        page_url = "https://www.tommybahama.com" + next_page[0]
        page_response = session.get(page_url)
        page_dom = etree.HTML(page_response.text)
        all_locations += page_dom.xpath(
            '//a[@class="store-finder-results-title"]/@href'
        )
        next_page = page_dom.xpath('//a[contains(text(), "Next")]/@href')

    for url in list(set(all_locations)):
        store_url = urljoin(start_url, url.split("?")[0])
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        if loc_dom.xpath('//a/img[contains(@alt, "taken you slightly off course")]'):
            continue

        raw_address = loc_dom.xpath(
            '//div[contains(text(), "Address")]/following-sibling::div/text()'
        )
        raw_address = [e.replace("\xa0", " ").strip() for e in raw_address if e.strip()]
        location_name = loc_dom.xpath('//h1[@class="page-title"]/text()')
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        street_address = raw_address[0]
        city = raw_address[1].split(", ")[0]
        state = raw_address[1].split(", ")[-1].split()[0]
        zip_code = raw_address[1].split(", ")[-1].split()[-1]
        country_code = re.findall(
            "storeaddresscountryname = '(.+?)';", loc_response.text
        )
        country_code = country_code[0] if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//div[@class="store-details-container"]//a/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = re.findall("storelatitude = '(.+?)';", loc_response.text)
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = re.findall("storelongitude = '(.+?)';", loc_response.text)
        longitude = longitude[0] if longitude else "<MISSING>"
        hoo = loc_dom.xpath(
            '//div[contains(text(), "Store Hours")]/following-sibling::div/text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        hoo = " ".join(hoo).split("Hours: ")[-1].split("This location")[0].strip()
        hours_of_operation = (
            hoo.split("Open to a limited")[0].strip() if hoo else "<MISSING>"
        )
        hours_of_operation = hours_of_operation.split(" Happy")[0]
        hours_of_operation = hours_of_operation.split(" Seating")[0]
        if "temporarily" in hours_of_operation:
            hours_of_operation = "Temporarily Closed"
        hours_of_operation = hours_of_operation.replace("|", "").replace(">br>", "")

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
