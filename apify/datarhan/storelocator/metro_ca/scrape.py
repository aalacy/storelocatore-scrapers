import re
import demjson
import csv
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


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

    DOMAIN = "metro.ca"
    start_url = "https://www.metro.ca/en/find-a-grocery"

    all_locations = []
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA],
        max_radius_miles=5,
        max_search_results=None,
    )
    for code in all_codes:
        formdata = {"postalCode": code + " 0A1", "provinceCode": "", "city": ""}
        headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }
        response = session.post(start_url, data=formdata, headers=headers)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//a[@class="fs--grocery-detail"]/@href')

    for url in list(set(all_locations)):
        store_url = urljoin(start_url, url)
        store_response = session.get(store_url)
        store_dom = etree.HTML(store_response.text)

        data = store_dom.xpath('//script[contains(text(), "storeJsonLd")]/text()')[0]
        data = data.replace("\\n", "").replace("\r\n", "").replace("\\", "")
        data = re.findall('storeJsonLd = "(.+)";', data)[0]
        data = demjson.decode(data)

        location_name = data["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = data["address"]["streetAddress"]
        street_address = (
            street_address.replace("&#39;", "'") if street_address else "<MISSING>"
        )
        city = data["address"]["addressLocality"]
        city = city if city else "<MISSING>"
        state = data["address"]["addressRegion"]
        state = state if state else "<MISSING>"
        zip_code = data["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = data["address"]["addressCountry"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = data["telephone"]
        phone = phone if phone else "<MISSING>"
        location_type = data["type"].split("/")[-1]
        latitude = data["geo"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = data["geo"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        for elem in data["openingHoursSpecification"]:
            day = elem["dayOfWeek"]
            opens = elem["opens"]
            closes = elem["closes"]
            hours_of_operation.append(f"{day} {opens} - {closes}")
        hours_of_operation = (
            ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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
        check = "{} {}".format(street_address, location_name)
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
