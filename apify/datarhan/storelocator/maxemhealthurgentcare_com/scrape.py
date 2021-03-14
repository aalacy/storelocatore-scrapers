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

    start_url = "https://maxemhealthurgentcare.com/locations-2/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="link"]/a/@href')
    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="post_title"]/text()')
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        raw_data = loc_dom.xpath(
            '//div[@class="profile_single_photo col-md-5"]/following-sibling::div[1]/p/text()'
        )
        raw_data = [e.strip() for e in raw_data if e.strip()]
        if len(raw_data) == 1:
            continue
        if "suit" in raw_data[1].lower():
            raw_data = [" ".join(raw_data[:2])] + raw_data[2:]
        street_address = raw_data[0].strip()
        city = raw_data[1].split(", ")[0].strip()
        state = raw_data[1].split(", ")[-1].split()[0].strip()
        zip_code = raw_data[1].split(", ")[-1].split()[-1].strip()
        if len(zip_code) == 2:
            zip_code = "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = raw_data[2].split(":")[-1].replace("Ph. ", "").strip()
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = raw_data[-3:]
        hoo = [e.strip() for e in hoo if e.strip() and "Fax" not in e]
        hoo = [e.strip() for e in hoo if e.strip() and "Ph:" not in e]
        hours_of_operation = " ".join(hoo).split(" Click")[0].strip() if hoo else "<MISSING>"

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
