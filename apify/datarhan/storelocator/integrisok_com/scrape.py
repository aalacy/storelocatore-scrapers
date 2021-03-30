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
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36"
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
        loc_response = session.get(store_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi.xpath('.//h3[@class="search-result-name"]/a/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath('//div[@class="address"]/text()')
        if not raw_address:
            raw_address = loc_dom.xpath('//p[@class="facility-p"]/text()')
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        if not raw_address:
            continue
        if len(raw_address) == 3:
            raw_address = [", ".join(raw_address[:2])] + raw_address[2:]
        street_address = raw_address[0]
        city = raw_address[-1].split(", ")[0]
        state = raw_address[-1].split(", ")[-1].split()[0]
        if state == "Oklahoma":
            city = " ".join(city.split()[:2])
        zip_code = raw_address[-1].split(", ")[-1].split()[-1]
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
        hoo = loc_dom.xpath(
            '//div[@class="page-summary-group component-hours"]//text()'
        )
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        if hoo and "Hours" in hoo[0]:
            hoo = hoo[1:-1]
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
