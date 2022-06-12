import re
import csv
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl


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

    start_url = "https://us.octobersveryown.com/pages/contact"
    domain = "octobersveryown.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//a[contains(text(), "STORES")]/following-sibling::ul[1]//a/@href'
    )
    for url in list(set(all_locations)):
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//div[@class="store-information"]/h1/text()')[0]
        raw_data = loc_dom.xpath('//div[@class="store-information"]/p/text()')
        addr = parse_address_intl(" ".join(raw_data[:3]))
        street_address = raw_data[0]
        city = addr.city
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = "<MISSING>"
        for e in raw_data:
            if "Tel" in e:
                phone = e.split(":")[-1].strip()
                break
        location_type = "<MISSING>"
        geo = re.findall(r"LatLng\((.+?)\);", loc_response.text)[0].split(", ")
        latitude = geo[0]
        longitude = geo[1]
        hoo = raw_data[3:]
        hoo = [e.strip() for e in hoo if "Tel" not in e]
        hours_of_operation = " ".join(hoo).split("Closed:")[0].strip()
        if "USA" in hours_of_operation:
            hours_of_operation = hours_of_operation.replace("USA", "")
            country_code = "USA"
        if "Temporarily closed" in hours_of_operation:
            hours_of_operation = "<MISSING>"
            location_type = "Temporarily closed"

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
