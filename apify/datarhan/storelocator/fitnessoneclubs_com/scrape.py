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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://fitnessoneclubs.com/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//a[contains(text(), "Locations")]/following-sibling::ul//a/@href'
    )
    for url in list(set(all_locations)):
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h1/span/text()")[0]
        raw_data = loc_dom.xpath('//a[contains(@href, "maps")]/span/text()')
        if not raw_data:
            raw_data = [
                loc_dom.xpath(
                    '//div[@class="py-3 px-10 my-4 text-center"]/p/span/text()'
                )[-1]
            ]
        raw_data = raw_data[0].replace("\xa0", ", ").split(", ")
        street_address = raw_data[0]
        city = raw_data[1]
        state = raw_data[-1].split()[0]
        zip_code = raw_data[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/span/text()')
        if not phone:
            phone = loc_dom.xpath(
                '//div[@class="py-3 px-10 my-4 text-center"]/p/span/text()'
            )[1:-1]
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = loc_dom.xpath('//a[contains(@href, "maps")]/@href')
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if geo:
            geo = geo[0].split("/@")[-1].split(",")[:2]
            latitude = geo[0]
            longitude = geo[1]
        hoo = loc_dom.xpath(
            '//div[h2[span[contains(text(), "Club Information")]]]/following-sibling::div[@class="size-md my-4"][1]/table[1]//text()'
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
