import csv
import json
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
    session = SgRequests()

    items = []

    DOMAIN = "integrisok.com"

    start_url = "https://integrisok.com/public/api/PublicApi/SearchLocations"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
    }
    formadata = {
        "Page": "0",
        "Page": "0",
        "Latitude": "",
        "Longitude": "",
        "RangeLatitude": "",
        "RangeLongitude": "",
        "Query": "",
        "Type": "",
        "ZipCode": "",
        "Range": "10",
        "Range": "10",
        "Sort": "Relevance",
        "Sort": "Relevance",
        "PageSize": "1000",
        "PageSize": "1000",
    }
    response = session.post(start_url, headers=headers, data=formadata)
    data = json.loads(response.text)
    dom = etree.HTML(data["Html"])

    all_poi = dom.xpath('//div[@class="search-result result-location"]')
    for poi in all_poi:
        store_url = poi.xpath('.//h3[@class="search-result-name"]/a/@href')
        store_url = store_url[0] if store_url else "<MISSING>"
        location_name = poi.xpath('.//h3[@class="search-result-name"]/a/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        address_raw = poi.xpath(
            './/h3[@class="search-result-name"]/following-sibling::div[1]//text()'
        )
        address_raw = [elem.strip() for elem in address_raw if elem.strip()]
        if not address_raw:
            continue
        street_address = address_raw[0]
        city = address_raw[-1].split(",")[0]
        state = address_raw[-1].split(",")[-1].strip().split()[0]
        zip_code = address_raw[-1].split(",")[-1].strip().split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi.xpath('.//div[@class="search-result-phone-location"]/a/text()')
        if phone:
            if len(phone[0].strip()) > 14:
                phone = phone[0].split()[0].split(",")
        phone = phone[0] if phone else "<MISSING>"
        location_type = poi.xpath('.//div[@class="category"]/text()')
        location_type = location_type[0].strip() if location_type else "<MISSING>"
        latitude = poi.xpath(".//div/@data-lat")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = poi.xpath(".//div/@data-lon")
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = "<MISSING>"

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
