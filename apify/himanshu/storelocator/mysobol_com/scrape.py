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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://mysobol.com/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=bcab98a9bf&load_all=1&layout=1"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        store_url = poi["website"]
        loc_response = session.get(store_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi["title"]
        street_address = poi["street"]
        city = poi["city"]
        state = poi["state"]
        zip_code = poi["postal_code"]
        country_code = poi["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["id"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        longitude = poi["lng"]
        hoo = loc_dom.xpath('//div[p[span[contains(text(), "Open 7 days")]]]//text()')
        if not hoo:
            hoo = loc_dom.xpath('//p[i[@class="far fa-clock"]]/text()')
        if not hoo:
            hoo = loc_dom.xpath(
                '//div[@class="fusion-text fusion-text-3 addressText"]//strong/text()'
            )
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo).replace("……….", " ") if hoo else "<MISSING>"

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
