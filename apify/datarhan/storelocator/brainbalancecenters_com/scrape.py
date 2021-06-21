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

    start_url = "https://www.brainbalancecenters.com/locations?zip="
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//li[@class="center js-center"]')
    for poi_html in all_locations:
        store_url = poi_html.xpath('.//a[contains(text(), "Visit Website")]/@href')[0]
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi_html.xpath('.//h2[@class="center-title"]/text()')[0].strip()
        raw_address = poi_html.xpath(
            './/div[@class="col-12 clearfix center-location"]/p/text()'
        )
        raw_address = [e.strip() for e in raw_address if e.strip()]
        if len(raw_address) == 3:
            street_address = " ".join(raw_address[:2])
        else:
            street_address = raw_address[0]
        street_address = street_address.split("(")[0].strip()
        city = raw_address[-1].split(", ")[0]
        state = " ".join(raw_address[-1].split(", ")[-1].split()[:-1])
        zip_code = raw_address[-1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//p[@class="phone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi_html.xpath("@data-lat")[0]
        longitude = poi_html.xpath("@data-lng")[0]
        hoo = loc_dom.xpath(
            '//p[contains(text(), "Hours")]/following-sibling::p/text()'
        )
        if not hoo:
            response = session.get(
                f"https://www.brainbalancecenters.com/locations?zip={zip_code}"
            )
            dom = etree.HTML(response.text)
            hoo = dom.xpath(
                '//div[div[h2[a[contains(text(), "{}")]]]]/following-sibling::div//h4[contains(text(), "Hours")]/following-sibling::*//text()'.format(
                    location_name
                )
            )
        hoo = [e.strip().replace("\n", " ") for e in hoo if e.strip()]
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
