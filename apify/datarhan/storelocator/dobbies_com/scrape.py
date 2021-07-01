import csv
from lxml import etree
from time import sleep
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from sgselenium.sgselenium import webdriver

profile = webdriver.FirefoxProfile()
profile.set_preference("geo.prompt.testing", True)
profile.set_preference("geo.prompt.testing.allow", True)
profile.set_preference(
    "geo.wifi.uri",
    'data:application/json,{"location": {"lat": 40.7590, "lng": -73.9845}, "accuracy": 27000.0}',
)
options = webdriver.FirefoxOptions()
options.headless = True


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

    DOMAIN = "dobbies.com"
    start_url = "https://www.dobbies.com/store-locator"

    with webdriver.Firefox(options=options, firefox_profile=profile) as driver:
        driver.get(start_url)
        sleep(5)
        driver.find_element_by_xpath(
            '//div[contains(text(), "See all stores")]'
        ).click()
        sleep(25)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//div[h2[contains(text(), "Store List")]]//a/@href')
    all_locations += dom.xpath('//a[contains(text(), "See all details")]/@href')
    for url in list(set(all_locations)):
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        if loc_response.status_code != 200:
            continue
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="ms-content-block__title"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_adr = loc_dom.xpath(
            '//h4[contains(text(), "Address")]/following-sibling::p[1]/text()'
        )[0]
        addr = parse_address_intl(raw_adr)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        street_address = street_address if street_address else "<MISSING>"
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//a[contains(@href, "tel")]//text()')
        phone = phone[-1] if phone else "<MISSING>"
        location_type = "<MISSING>"
        tmp_closed = loc_dom.xpath(
            '//h3[contains(text(), "Our restaurant is temporarily closed")]'
        )
        if tmp_closed:
            location_type = "temporarily closed"
        geo = loc_dom.xpath('//a[contains(@href, "/maps/")]/@href')
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if geo:
            geo = geo[0].split("/@")[-1].split(",")[:2]
            latitude = geo[0]
            longitude = geo[1]
        hours_of_operation = loc_dom.xpath(
            '//h3[contains(text(), "Store opening hours")]/following-sibling::ul/li//text()'
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
