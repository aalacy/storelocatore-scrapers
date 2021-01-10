import csv
from time import sleep
from lxml import etree

from sgrequests import SgRequests
from sgselenium import SgChrome


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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []

    DOMAIN = "allenedmonds.com"
    start_url = "https://www.allenedmonds.com/stores"

    with SgChrome() as driver:
        driver.get(start_url)
        sleep(2)
        driver.find_element_by_id("dwfrm_storelocator_maxdistance").click()
        sleep(2)
        driver.find_element_by_xpath('//option[@label="USA"]').click()
        sleep(2)
        driver.find_element_by_id("dwfrm_storelocator_postalCode").send_keys("10001")
        sleep(2)
        driver.find_element_by_name("dwfrm_storelocator_findbyzip").click()
        sleep(2)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//a[@class="store-link"]/@href')
    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//div[@id="primary"]/h1/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = loc_dom.xpath('//span[@itemprop="streetAddress"]/text()')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')
        city = city[0] if city else "<MISSING>"
        state = loc_dom.xpath('//span[@itemprop="addressRegion"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = loc_dom.xpath('//span[@itemprop="addressCountry"]/text()')
        country_code = country_code[0] if country_code else "<MISSING>"
        if country_code == "Italy":
            continue
        store_number = loc_dom.xpath('//input[@name="storeid"]/@value')
        store_number = store_number[0] if store_number else "<MISSING>"
        phone = loc_dom.xpath('//span[@itemprop="telephone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = loc_dom.xpath("//div/@itemtype")[0].split("/")[-1]
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = loc_dom.xpath(
            '//h2[contains(text(), "Hours:")]/following-sibling::p[2]//text()'
        )
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
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
