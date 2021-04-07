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

    start_url = "http://ccscoffee.com/locations/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div//li/a[contains(@href, "locations")]/@href')
    for store_url in all_locations:
        if "http" not in store_url:
            continue
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h2[@class="h3"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath("//address/text()")
        raw_address = [e.strip() for e in raw_address]
        street_address = raw_address[0]
        city = raw_address[1].split(", ")[0]
        state = raw_address[1].split(", ")[-1].split()[0]
        zip_code = raw_address[1].split(", ")[-1].split()[-1]
        zip_code = zip_code if zip_code else "<MISSING>"
        if len(zip_code) > 5:
            zip_code = "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath(
            '//h5[contains(text(), "Phone")]/following-sibling::dl[1]/dt/text()'
        )
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = re.findall(r"LatLng\((.+?)\)", loc_response.text)[-1].split(",")
        latitude = geo[0]
        longitude = geo[1]
        hoo = loc_dom.xpath(
            '//h5[contains(text(), "Hours of Operation")]/following-sibling::dl[2]/dt/text()'
        )
        hoo = [e.strip().replace("\n", "") for e in hoo if e.strip()]
        hours_of_operation = (
            " ".join(hoo).replace("Spring 2021 Hours of Operation ", "")
            if hoo
            else "<MISSING>"
        )

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
