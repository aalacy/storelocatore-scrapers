import csv
from lxml import etree

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
    session = SgRequests()

    DOMAIN = "eagletransmission.com"

    start_url = "https://eagletransmission.com/locations/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }
    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(text(), "View shop hours")]/@href')
    for store_url in list(set(all_locations)):
        loc_response = session.get(store_url, headers=headers)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//div[@class="adres"]/h2/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath('//div[@class="adrs-call"]/p/text()')
        city = raw_address[-1].split(",")[0].strip()
        street_address = raw_address[0]
        state = raw_address[-1].split(",")[-1].split(".")[0].strip().split()[0].upper()
        zip_code = raw_address[-1].split(",")[-1].split(".")[-1].split()[-1].strip()
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//span/a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = (
            loc_dom.xpath("//iframe/@src")[0]
            .split("!2d")[1]
            .split("!2m")[0]
            .split("!3d")
        )
        latitude = geo[-1]
        longitude = geo[0]
        hoo = loc_dom.xpath('//div[@class="adres hrs"]/p[2]//text()')
        hoo = [e.strip() for e in hoo if e.strip()]
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

        yield item


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
