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

    store_url = "https://growlerusa.com/craft-beer-pubs/tx-austin-ut/"
    domain = "growlerusa.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(store_url, headers=hdr)
    dom = etree.HTML(response.text)

    location_name = dom.xpath('//div[@class="et_pb_text_inner"]/h2/text()')[-1]
    raw_address = dom.xpath('//a[@title="Map Link"]/text()')
    street_address = raw_address[0]
    city = raw_address[-1].split(", ")[0]
    state = raw_address[-1].split(", ")[-1].split()[0]
    zip_code = raw_address[-1].split(", ")[-1].split()[-1]
    country_code = "<MISSING>"
    store_number = "<MISSING>"
    phone = dom.xpath('//a[contains(@href, "tel")]/text()')
    phone = phone[0] if phone else "<MISSING>"
    location_type = "<MISSING>"
    geo = (
        dom.xpath('//a[contains(@href, "/maps/")]/@href')[-1]
        .split("/@")[-1]
        .split(",")[:2]
    )
    latitude = geo[0]
    longitude = geo[-1]
    hoo = dom.xpath('//h3[contains(text(), "HOURS")]/following-sibling::p[1]//text()')
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
