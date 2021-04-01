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

    session = SgRequests()

    DOMAIN = "tommybahama.com"
    start_url = "https://www.tommybahama.com/en/store-finder?q=&searchStores=false&searchRestaurants=true&searchOutlets=false&searchInternational=true&CSRFToken=b6ba6d9c-9bc3-48f3-952d-2f59a53a4656"
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//span[@class="store-restaurant-header"]/a/@href')
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
        if url == "#":
            continue
        if "/store/" in url:
            continue
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h3[@class="cmp-title__text"]/text()')
        location_name = (
            location_name[0].strip() if location_name[0].strip() else "<MISSING>"
        )
        street_address = loc_dom.xpath(
            '//p[*[*[a[contains(@href, "/maps/")]]]]/preceding-sibling::p[3]/text()'
        )
        street_address = street_address[0] if street_address else "<MISSING>"
        city = loc_dom.xpath(
            '//p[*[*[a[contains(@href, "/maps/")]]]]/preceding-sibling::p[2]/text()'
        )[0].split(", ")[0]
        state = (
            loc_dom.xpath(
                '//p[*[*[a[contains(@href, "/maps/")]]]]/preceding-sibling::p[2]/text()'
            )[0]
            .split(",")[-1]
            .split()[0]
        )
        zip_code = (
            loc_dom.xpath(
                '//p[*[*[a[contains(@href, "/maps/")]]]]/preceding-sibling::p[2]/text()'
            )[0]
            .split(",")[-1]
            .split()[-1]
        )
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//p[contains(text(), "Phone")]/text()')
        if phone:
            phone = phone[0].replace("Phone: ", "")
        if not phone:
            phone = loc_dom.xpath(
                '//p[b[contains(text(), "Store")]]/following-sibling::p[1]/b/text()'
            )
            phone = phone[0] if phone else ""
        if not phone:
            phone = loc_dom.xpath(
                '//p[contains(text(), "Restaurant & Bar")]/following-sibling::p[1]/text()'
            )
            phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = (
            loc_dom.xpath('//p[contains(text(), "Open:")]/text()')[-1]
            .replace("Open:", "")
            .replace("|", ",")
        )
        if not hours_of_operation:
            hours_of_operation = (
                loc_dom.xpath('//p[contains(text(), "Open:")]/text()')[0]
                .replace("Open:", "")
                .replace("|", ",")
            )
        hours_of_operation = (
            hours_of_operation if hours_of_operation else "<INACCESSIBLE>"
        )

        if "COCONUT" in location_name:
            phone = "239.947.2203"

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
