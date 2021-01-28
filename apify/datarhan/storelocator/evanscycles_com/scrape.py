import csv
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgselenium import SgFirefox


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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

    DOMAIN = "evanscycles.com"
    start_url = "https://www.evanscycles.com/stores/all"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
    }
    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//div[@class="letItems"]/a/@href')
    for url in all_locations:
        store_url = urljoin(start_url, url.lower())
        loc_response = session.get(store_url, headers=headers)
        loc_dom = etree.HTML(loc_response.text)

        location_name = [
            elem.strip()
            for elem in loc_dom.xpath('//div[@id="StoreDetailsContainer"]/h1/text()')
            if elem.strip()
        ]
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = loc_dom.xpath(
            '//div[@itemprop="address"]/following-sibling::div[1]/text()'
        )
        street_address = [elem.strip() for elem in street_address if elem.strip()]
        street_address = " ".join(street_address) if street_address else "<MISSING>"
        city = loc_dom.xpath(
            '//div[@itemprop="address"]/following-sibling::div[2]/text()'
        )
        city = city[0].strip() if city[0].strip() else "<MISSING>"
        state = "<MISSING>"
        zip_code = loc_dom.xpath(
            '//div[@itemprop="address"]/following-sibling::div[4]/text()'
        )
        zip_code = zip_code[0].strip() if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = store_url.split("-")[-1]
        phone = loc_dom.xpath('//span[@itemprop="telephone"]/text()')
        phone = phone[0].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = loc_dom.xpath(
            '//meta[@itemprop="openingHours"]/following-sibling::span/text()'
        )
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

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
