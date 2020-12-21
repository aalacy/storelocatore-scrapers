import re
import csv
from lxml import etree

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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []

    DOMAIN = "flyersenergy.com"
    start_url = "https://www.flyersenergy.com/locations/"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36"
    }

    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="wpb_wrapper"]/p/a/@href')

    for store_url in all_locations:
        store_response = session.get(store_url)
        store_dom = etree.HTML(store_response.text)
        location_name = store_dom.xpath(
            '//div[@class="title_subtitle_holder"]//span/text()'
        )
        location_name = location_name[0] if location_name else "<MISSING>"
        address_raw = store_dom.xpath(
            '//div[contains(@class, "wpb_text_column wpb_content_element")]/div[h3]/p[1]/text()'
        )
        if address_raw:
            if len(address_raw) == 3:
                address_raw = [
                    ", ".join(address_raw[:2]).replace("\n", "")
                ] + address_raw[2:]
            street_address = address_raw[0]
            street_address = street_address if street_address else "<MISSING>"
            city = address_raw[1].split(",")[0].strip()
            state = address_raw[1].split(",")[-1].split()[0]
            zip_code = address_raw[1].split(",")[-1].split()[-1]
            geo = re.findall("2d(.+)!2m", store_dom.xpath("//iframe/@src")[-1])
            if not geo:
                geo = (
                    re.findall("2d(.+)!3m", store_dom.xpath("//iframe/@src")[-1])[0]
                    .split("!3m2")[0]
                    .split("!3d")
                )
            else:
                geo = geo[0].split("!3d")
            latitude = geo[1]
            longitude = geo[0]
        else:
            street_address = "<MISSING>"
            city = "<MISSING>"
            state = "<MISSING>"
            zip_code = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = store_dom.xpath(
            '//div[contains(@class, "wpb_text_column wpb_content_element")]/div[h3]/p[3]/text()'
        )
        phone = phone[0].split(":")[-1].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = store_dom.xpath(
            '//div[contains(@class, "wpb_text_column wpb_content_element")]/div[h3]/p[2]/text()'
        )
        hours_of_operation = (
            hours_of_operation[-1].strip() if hours_of_operation else "<MISSING>"
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
