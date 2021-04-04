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
    session = SgRequests().requests_retry_session(retries=0)

    items = []

    DOMAIN = "mimiscafe.com"

    start_url = "https://www.mimiscafe.com/locations/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }
    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(text(), "Learn More")]/@href')
    for url in all_locations:
        store_url = "https://" + url
        store_response = session.get(store_url, headers=headers)
        store_dom = etree.HTML(store_response.text)

        location_name = store_dom.xpath('//section[@class="content-holder"]//h1/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = store_dom.xpath("//section//address/text()")[0]
        city = (
            store_dom.xpath("//section//address/text()")[-1]
            .split(", ")[0]
            .strip()
            .capitalize()
        )
        if len(city.split()) > 2:
            city = street_address.split(", ")[1]
            street_address = street_address.split(", ")[0]
        if len(city.split()[0]) == 2:
            city = location_name
            street_address = street_address.replace(city, "")
        state = (
            store_dom.xpath("//section//address/text()")[-1].split(", ")[-1].split()[0]
        )
        zip_code = (
            store_dom.xpath("//section//address/text()")[-1].split(", ")[-1].split()[-1]
        )
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = store_dom.xpath('//li[contains(text(), "Phone:")]/a/text()')
        phone = phone[0] if phone else "<MISSING>"
        latitude = re.findall('data-lat="(.+)" data', store_response.text)
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = re.findall('data-lng="(.+)">', store_response.text)
        longitude = longitude[0] if longitude else "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = store_dom.xpath(
            '//h3[contains(text(), "Hours of Operation")]/following-sibling::ul/li/text()'
        )
        hours_of_operation = [elem.strip() for elem in hours_of_operation]
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
