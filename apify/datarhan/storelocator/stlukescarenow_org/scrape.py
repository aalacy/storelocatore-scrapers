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

    start_url = "https://findalocation.slhn.org/practice?theme=dir_sluhn&type=20"
    domain = "stlukescarenow.org"
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="provider-name"]/a/@href')
    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//div[@class="label"]/text()')
        if not location_name:
            location_name = loc_dom.xpath('//h1[@class="provider-name"]/text()')
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        street_address = loc_dom.xpath('//div[@class="line1"]/text()')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = loc_dom.xpath('//div[@class="citystate"]/text()')[0].split(", ")[0]
        state = loc_dom.xpath('//div[@class="citystate"]/text()')[0].split(", ")[1]
        zip_code = loc_dom.xpath('//div[@class="citystate"]/text()')[0].split(", ")[-1]
        country_code = "<MISSING>"
        store_number = loc_dom.xpath('//link[@rel="canonical"]/@href')[0].split("/")[-1]
        phone = loc_dom.xpath(
            '//div[@class="provider-top-details practice-top-details"]//a[contains(@href, "tel")]/text()'
        )
        phone = phone[0].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = loc_dom.xpath("//@data-lat")[0]
        longitude = loc_dom.xpath("//@data-long")[0]
        hoo = loc_dom.xpath('//div[label[contains(text(), "Hours")]]//text()')
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
