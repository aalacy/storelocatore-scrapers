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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []
    scraped_items = []

    start_url = "https://www.foodbasics.ca/find-your-food-basics.en.html"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = []
    all_towns = dom.xpath('//select[@name="town"]/option/@value')
    for town in all_towns:
        formdata = {
            "rechercher": "1",
            "postalCode1": "",
            "postalCode2": "",
            "searchMode": "town",
            "town": town,
            "method.search": "Recherche",
        }
        response = session.post(start_url, data=formdata)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//section[@class="store"]')

    for poi_html in all_locations:
        raw_data = poi_html.xpath('//p[@class="si-info"]/text()')
        raw_data = [e.strip() for e in raw_data if e.strip()]
        store_url = "https://www.foodbasics.ca/find-your-food-basics.en.html"
        location_name = raw_data[0]
        street_address = raw_data[1]
        city = raw_data[2]
        state = "<MISSING>"
        zip_code = raw_data[3]
        country_code = "CA"
        store_number = "<MISSING>"
        phone = raw_data[-1].strip()
        phone = phone if phone else "<MISSING>"
        if len(phone) < 10:
            phone = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = poi_html.xpath('.//div[@class="store-hours"]//text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo[1:]) if hoo else "<MISSING>"

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
