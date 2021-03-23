import re
import csv
from lxml import etree
from urllib.parse import urljoin

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
    scraped_items = []

    start_url = "https://www.burritoboyz.ca/toronto"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")

    hdr = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_cities = dom.xpath(
        '//label[contains(text(), "Locations")]/following-sibling::div//a/@href'
    )
    for url in all_cities:
        store_url = urljoin(start_url, url)
        response = session.get(store_url, headers=hdr)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath('//div[div[div[h3[contains(text(), "LOCATION")]]]]')
        all_locations += dom.xpath(
            '//div[div[div[h3[strong[contains(text(), "LOCATION")]]]]]'
        )
        if "etobicoke" in response.url:
            all_locations += dom.xpath(
                '//div[@data-block-type="2" and div[h3[contains(text(), "LOCATION")]]]'
            )[-1]

        for poi_html in all_locations:
            raw_data = poi_html.xpath(".//p/text()")
            if len(raw_data) > 20:
                continue
            addr = parse_address_intl(
                " ".join([e for e in raw_data[:2] if "am -" not in e])
            )
            location_name = raw_data[0].split(",")[0]
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            city = city if city else "<MISSING>"
            state = addr.state
            state = state if state else "<MISSING>"
            zip_code = addr.postcode
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = "CA"
            store_number = "<MISSING>"
            location_type = "<MISSING>"
            phone = poi_html.xpath(
                './/following-sibling::div//h3[contains(text(), "PHONE")]/following-sibling::p[1]/text()'
            )
            if not phone:
                phone = poi_html.xpath(
                    './/following-sibling::div//h3[contains(text(), "Phone")]/following-sibling::p[1]/text()'
                )
            if not phone:
                phone = poi_html.xpath(
                    './/following-sibling::div//h3[contains(text(), "PHONE")]/following-sibling::p[1]/text()'
                )
            if not phone:
                phone = poi_html.xpath(
                    './/preceding-sibling::div//h3[contains(text(), "PHONE")]/following-sibling::p[1]/text()'
                )
            phone = phone[0] if phone else "<MISSING>"
            if phone == "TBD":
                phone = "<MISSING>"
                location_type = "coming soon"
            if phone == "<MISSING>" and street_address == "3355 Bloor St W":
                phone = "(416) 763-2699"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hoo = poi_html.xpath(
                './/following-sibling::div//h3[contains(text(), "HOURS")]/following-sibling::p//text()'
            )
            if not hoo:
                hoo = poi_html.xpath(
                    './/following-sibling::div//h3[contains(text(), "Hours")]/following-sibling::p//text()'
                )
            if not hoo:
                hoo = poi_html.xpath(
                    './/h3[contains(text(), "HOURS")]/following-sibling::p//text()'
                )
            if not hoo:
                hoo = poi_html.xpath(
                    './/h3[strong[contains(text(), "HOURS")]]/following-sibling::p//text()'
                )
            if not hoo:
                hoo = poi_html.xpath(
                    './/preceding-sibling::div//h3[strong[contains(text(), "HOURS")]]/following-sibling::p//text()'
                )
            if not hoo:
                hoo = poi_html.xpath(
                    './/following-sibling::div//h3[strong[contains(text(), "HOURS")]]/following-sibling::p//text()'
                )
            hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
