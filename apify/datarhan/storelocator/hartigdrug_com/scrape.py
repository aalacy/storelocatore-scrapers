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

    DOMAIN = "hartigdrug.com"
    start_url = "https://www.hartigdrug.com/stores"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//a[contains(text(), "More Info")]/@href')

    for url in list(set(all_locations)):
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@id="page-title"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = loc_dom.xpath(
            '//div[contains(text(), "Address:")]/following-sibling::div/text()'
        )
        street_address = street_address[0] if street_address else "<MISSING>"
        raw_data = loc_dom.xpath(
            '//div[@class="field field-name-field-address-two"]/text()'
        )
        if raw_data:
            raw_data = raw_data[0]
            city = raw_data.split(", ")[0]
            state = raw_data.split(", ")[-1].split()[0]
            zip_code = raw_data.split(", ")[-1].split()[-1]
            store_number = loc_dom.xpath(
                '//div[contains(text(), "Store Number:")]/following-sibling::div/text()'
            )
            store_number = store_number[0] if store_number else "<MISSING>"
            phone = loc_dom.xpath(
                '//div[contains(text(), "Phone:")]/following-sibling::div/text()'
            )
            phone = phone[0] if phone else "<MISSING>"
            hoo = loc_dom.xpath(
                '//h3[contains(text(), "Store Hours")]/following-sibling::p/text()'
            )
            hoo = [elem.strip() for elem in hoo if elem.strip()]
            hoo = " ".join(hoo) if hoo else "<MISSING>"
        else:
            street_address = loc_dom.xpath('//span[@class="address1"]/text()')
            if not street_address:
                street_address = dom.xpath(
                    '//td[@class="views-field views-field-field-address" and a[@href="{}"]]/a/text()'.format(
                        store_url
                    )
                )[0]
                city = "<MISSING>"
                state = "<MISSING>"
                zip_code = "<MISSING>"
                store_number = "<MISSING>"
                phone = dom.xpath(
                    '//td[@class="views-field views-field-field-home-phone" and a[@href="{}"]]/a/text()'.format(
                        store_url
                    )
                )[0]
                hoo = "<MISSING>"
            else:
                street_address = street_address[0].replace("|", "").strip()
                city = loc_dom.xpath('//span[@class="city"]/text()')[0][:-1].strip()
                state = loc_dom.xpath('//span[@class="region"]/text()')[0].strip()
                zip_code = loc_dom.xpath('//span[@class="postalcode"]/text()')[0]
                store_number = "<MISSING>"
                phone = loc_dom.xpath('//div[@class="phone"]/a/text()')[-1]
                hoo = "<MISSING>"
        country_code = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"

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
            hoo,
        ]

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
