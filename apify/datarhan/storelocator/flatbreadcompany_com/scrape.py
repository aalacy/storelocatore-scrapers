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

    start_url = "https://flatbreadcompany.com/locations/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@class="location col-sm-6 col-md-4 align_center"]/a/@href'
    )
    for store_url in all_locations:
        loc_response = session.get(store_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//div[@class="title-wrapper"]/div[1]/text()')
        if not location_name:
            location_name = re.findall("The (.+?) Story", loc_response.text)
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        raw_address = loc_dom.xpath('//span[@class="media-body"]/span/text()')[:2]
        raw_address = [e.strip() for e in raw_address]
        street_address = raw_address[0]
        city = raw_address[-1].split(", ")[0]
        state = raw_address[-1].split(", ")[-1].split()[0]
        zip_code = " ".join(raw_address[-1].split(", ")[-1].split()[1:])
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//p[@class="res-number"]/a/text()')
        phone = phone[0] if phone else "<MISSING>"
        if "Please use email" in phone:
            phone = "<MISSING>"
        location_type = "<MISSING>"
        geo = loc_dom.xpath('//div[@class="media item"]/a/@href')[0]
        if "/@" in geo:
            geo = geo.split("/@")[-1].split(",")[:2]
        else:
            geo = (
                loc_dom.xpath('//div[@class="media item"]/a/@href')[0]
                .split("ll=")[-1]
                .split("&")[0]
                .split(",")
            )
        latitude = geo[0]
        longitude = geo[1]
        hoo = hoo = loc_dom.xpath('//ul[@class="res-date-time"]//text()')
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
