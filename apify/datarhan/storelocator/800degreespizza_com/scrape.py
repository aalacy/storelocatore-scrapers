import re
import csv
from lxml import etree
from time import sleep
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgselenium import SgFirefox
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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://800degrees.com/locations/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@class="elementor-widget-wrap" and div[div[h3[@class="elementor-heading-title elementor-size-default"]]]]'
    )
    for poi_html in all_locations:
        store_url = poi_html.xpath('.//a[@class="view-locate"]/@href')
        store_url = urljoin(start_url, store_url[0]) if store_url else "<MISSING>"
        raw_address = " ".join(
            poi_html.xpath(
                './/h4[contains(text(), "Address")]/following-sibling::div[1]/text()'
            )
        ).replace("\n", ", ")
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        city = addr.city
        location_name = poi_html.xpath(".//h3/text()")[0].strip()
        if "(" in location_name:
            street_address = raw_address.split(", ")[0]
        if not city and "(" in location_name:
            city = re.findall(r"\((.+?)\)", location_name)[0]
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//a[contains(@href, "tel")]/b/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        if poi_html.xpath('.//h4[contains(text(), "TEMPORARILY CLOSED")]'):
            location_type = "TEMPORARILY CLOSED"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if store_url != "<MISSING>":
            with SgFirefox() as driver:
                driver.get(store_url)
                sleep(20)
                try:
                    driver.switch_to.frame(
                        driver.find_element_by_id("content-mask-frame")
                    )
                except Exception:
                    driver.switch_to.frame(
                        driver.find_element_by_xpath(
                            '//div[@class="rewards-locate"]/p/iframe'
                        )
                    )
                loc_dom = etree.HTML(driver.page_source)
                try:
                    geo = (
                        loc_dom.xpath('//a[contains(@href, "maps?ll=")]/@href')[0]
                        .split("ll=")[-1]
                        .split("&")[0]
                        .split(",")
                    )
                except Exception:
                    try:
                        driver.switch_to.frame(
                            driver.find_element_by_xpath('//div[@id="mapDiv"]//iframe')
                        )
                        loc_dom = etree.HTML(driver.page_source)
                        geo = (
                            loc_dom.xpath('//a[contains(@href, "maps?ll=")]/@href')[0]
                            .split("ll=")[-1]
                            .split("&")[0]
                            .split(",")
                        )
                    except Exception:
                        geo = ["<MISSING>", "<MISSING>"]
                latitude = geo[0]
                longitude = geo[1]
        hoo = poi_html.xpath(
            './/h4[contains(text(), "Hours")]/following-sibling::div[1]//text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = (
            " ".join(hoo).replace("View Location", "").strip() if hoo else "<MISSING>"
        )
        if not hours_of_operation:
            hours_of_operation = "<MISSING>"
        if "– — – Coming" in hours_of_operation:
            continue

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
