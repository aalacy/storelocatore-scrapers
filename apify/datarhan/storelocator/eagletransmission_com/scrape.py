import csv
from urllib.parse import urljoin
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_usa


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

    start_url = "https://eagletransmission.com/location"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }
    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//h5[@class="big"]/a/@href')
    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url, headers=headers)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h2[@class="sub-heading"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address_raw = loc_dom.xpath('//p[@class="adress"]/text()')[0]
        raw_address = parse_address_usa(raw_address_raw)
        city = raw_address.city
        if "Bvld." in raw_address_raw:
            street_address = raw_address_raw.split("Bvld.")[0] + "Bvld."
        else:
            street_address = raw_address_raw.split(city)[0].strip()
        state = raw_address.state
        zip_code = raw_address.postcode
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//p[@class="adress"]/text()')[-1].split()[-1]
        location_type = "<MISSING>"
        geo = (
            loc_dom.xpath('//a[contains(@href, "google.com/maps")]/@href')[0]
            .split("/@")[-1]
            .split(",1")[0]
        )
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if len(geo) == 2:
            latitude = geo[0]
            longitude = geo[1]
        hours_of_operation = "".join(
            loc_dom.xpath('//p[@class="adress"]/text()')[1:-1]
        ).strip()
        hours_of_operation = hours_of_operation.replace("Store Hours: ", "")

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
