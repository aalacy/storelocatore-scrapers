import re
import csv
import json
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

    DOMAIN = "slugandlettuce.co.uk"
    start_url = "https://www.slugandlettuce.co.uk/heremapssearch"
    headers = {
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
        "x-newrelic-id": "UgACU15WGwIDXVVbBAICVQ==",
        "x-requested-with": "XMLHttpRequest",
    }

    all_locations = []
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.BRITAIN],
        max_radius_miles=200,
        max_search_results=None,
    )
    for code in all_codes:
        formdata = {
            "postcode": code,
        }
        response = session.post(start_url, data=formdata, headers=headers)
        data = json.loads(response.text)
        dom = etree.HTML(data["results"])
        all_locations += dom.xpath('//div[@class="result"]')

    for poi_html in all_locations:
        store_url = poi_html.xpath('.//a[contains(text(), "Visit Website")]/@href')
        store_url = urljoin(start_url, store_url[0])
        location_name = poi_html.xpath('.//h3[@class="section-title"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        address_raw = poi_html.xpath(
            './/ul[@class="menu vertical venue-details"]/li[1]/div//text()'
        )
        address_raw = [elem.strip() for elem in address_raw if elem.strip()]
        street_address = address_raw[0]
        city = address_raw[1].split("-")[0].strip()
        state = address_raw[2]
        zip_code = address_raw[-1]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"

        check = f"{location_name} {street_address}"
        if check in scraped_items:
            continue
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        latitude = re.findall(r"lat: (.+?),", loc_response.text)
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = re.findall(r"lng: (.+?) }", loc_response.text)
        longitude = longitude[-1].strip() if longitude else "<MISSING>"
        hoo = loc_dom.xpath(
            '//h2[contains(text(), "Opening Times")]/following-sibling::div//text()'
        )
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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

        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
