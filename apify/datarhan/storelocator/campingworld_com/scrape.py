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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []

    DOMAIN = "campingworld.com"
    start_url = "https://rv.campingworld.com/locationsbystate"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }
    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="section-content"]//li/a/@href')

    for url in all_locations:
        base_url = "https://rv.ganderoutdoors.com/dealer/"
        store_url = urljoin(base_url, url)
        location_name = ""
        while not location_name:
            store_response = session.get(store_url.replace(" ", "%20"), headers=headers)
            store_dom = etree.HTML(store_response.text)
            location_name = store_dom.xpath(
                '//div[@class="col-xs-12 address"]/a/h1/text()'
            )

        location_name = location_name[0] if location_name else "<MISSING>"
        if "Camping World" not in location_name:
            continue
        address_raw = store_dom.xpath('//div[@class="col-xs-12 address"]/a/p/text()')
        address_raw = [elem.strip() for elem in address_raw if elem.strip()]
        street_address = address_raw[0]
        city = address_raw[1].split(", ")[0]
        state = address_raw[1].split(", ")[-1].split()[0]
        zip_code = address_raw[1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = store_dom.xpath('//a[@class="phone-number"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = store_dom.xpath('//meta[@name="geo.position"]/@content')[0].split(
            ";"
        )[0]
        longitude = store_dom.xpath('//meta[@name="geo.position"]/@content')[0].split(
            ";"
        )[1]
        hoo = store_dom.xpath(
            '//div[@id="dealerHours"]/div[@class="storehours"]//div[@class="row hours-row"]//text()'
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
