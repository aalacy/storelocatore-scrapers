import re
import csv
from lxml import etree
from time import sleep

from sgrequests import SgRequests
from sgselenium import SgFirefox


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

    start_url = "https://www.lonestarnationalbank.com/locations/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(5)
        search_zone = driver.find_element_by_id("search-section")
        driver.execute_script("arguments[0].scrollIntoView();", search_zone)
        driver.execute_script("arguments[0].click();", search_zone)
        search_zone.location_once_scrolled_into_view

        all_locations = dom.xpath('//div[@class="search-result "]')
        for poi_html in all_locations:
            store_url = start_url
            location_name = poi_html.xpath(".//h5/text()")
            location_name = location_name[0].strip() if location_name else "<MISSING>"

            more_info = driver.find_element_by_xpath(
                '//h5[contains(text(), "{}")]/following-sibling::span[@class="link"]'.format(
                    location_name
                )
            )
            sleep(2)
            driver.execute_script("arguments[0].scrollIntoView();", more_info)
            sleep(2)
            driver.execute_script("scrollBy(0,250);")
            more_info.click()

            loc_dom = etree.HTML(driver.page_source)

            adress_raw = poi_html.xpath('.//div[@class="search-result__body"]/p/text()')
            adress_raw = [e.strip() for e in adress_raw if e != "," and e.strip()]
            street_address = adress_raw[0]
            city = adress_raw[1]
            state = adress_raw[-2]
            zip_code = adress_raw[-1]
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            phone = loc_dom.xpath(
                '//div[@class="location-display"]//a[contains(@href, "tel")]/@href'
            )
            location_type = "<MISSING>"
            if not phone:
                location_type = "coming soon"
            phone = (
                phone[0].split(":")[-1]
                if phone and phone[0].split(":")[-1]
                else "<MISSING>"
            )
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hoo = loc_dom.xpath(
                '//div[@class="location-display"]//h5[contains(text(), "Lobby Hours")]/following-sibling::*//text()'
            )
            hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = (
                " ".join(hoo).split("Motor Bank")[0].strip() if hoo else "<MISSING>"
            )

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

            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
