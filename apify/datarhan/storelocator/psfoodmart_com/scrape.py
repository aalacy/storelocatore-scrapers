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
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "psfoodmart.com"
    start_url = "https://psfoodmart.com/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath("//h3/a/@href")

    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//div[@class="location-inner"]/h1/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath('//div[@class="location-inner"]/h3/text()')
        raw_address = " ".join([elem.strip() for elem in raw_address])
        street_address = raw_address.split(", ")[0].split("\n")[0]
        city = raw_address.split(", ")[0].split("\n")[-1]
        state = raw_address.split(", ")[-1].split()[0]
        zip_code = raw_address.split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = store_url.split("-")[-1]
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        data = loc_dom.xpath('//script[contains(text(), "properties = ")]/text()')[0]
        latitude = re.findall(
            r"properties =(.+?)],", data.replace("\n", "").replace("\t", "")
        )[0].split(",")[-2]
        longitude = re.findall(
            r"properties =(.+?)],", data.replace("\n", "").replace("\t", "")
        )[0].split(",")[-3]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = loc_dom.xpath(
            '//p[contains(text() ,"Operation Hours:")]/text()'
        )
        hours_of_operation = [elem.strip() for elem in hours_of_operation]
        hours_of_operation = (
            " ".join(hours_of_operation)
            .replace("\n", " ")
            .replace("Operation Hours: ", "")
            .split("What")[0]
            if hours_of_operation
            else "<MISSING>"
        )

        # Exceptions
        if "," in city:
            zip_code = city.split(",")[-1].split()[-1]
            state = city.split(",")[-1].split()[0]
            city = city.split(",")[0]
        if state.isdigit():
            state = "<MISSING>"
        if len(city.split()) > 2:
            city = city.split()[-1]

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

        if store_number not in scraped_items:
            scraped_items.append(store_number)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
