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

    start_url = "https://www.rituals.com/on/demandware.store/Sites-US-Site/en_US/Stores-FilterStores"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")

    hdr = {
        "content-type": "application/json",
        "x-requested-with": "XMLHttpRequest",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    }
    all_locations = []
    countries = ["US", "GB"]
    for country in countries:
        formdata = '{"latitude":"","longitude":"","countryCode":"%s","filterPostalCode":"","filterCity":"","filterCountryCode":"%s","searchText":"","nextPageToken":%s,"storeType":"normal","checkStoreAvailability":false}'
        page = 0
        response = session.post(
            start_url, data=formdata % (country, country, str(page)), headers=hdr
        )
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//div[@class="store js-store-item"]')
        next_page = dom.xpath('//a[contains(text(), "More Stores")]')
        while next_page:
            page += 5
            response = session.post(
                start_url, data=formdata % (country, country, str(page)), headers=hdr
            )
            dom = etree.HTML(response.text)
            all_locations += dom.xpath('//div[@class="store js-store-item"]')
            next_page = dom.xpath('//a[contains(text(), "More Stores")]')

    for poi_html in all_locations:
        store_url = poi_html.xpath('.//a[@class="store-info-link"]/@href')
        store_url = urljoin(start_url, store_url[0]) if store_url else "<MISSING>"
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = " ".join(poi_html.xpath(".//h2/text()")[0].strip().split())
        raw_address = poi_html.xpath('.//div[@class="store-address"]//text()')
        raw_address = [e.strip() for e in raw_address if e.strip()]
        addr = parse_address_intl(" ".join(raw_address[:-1]))
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        street_address = street_address if street_address else "<MISSING>"
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = raw_address[-1]
        location_type = "<MISSING>"
        latitude = loc_dom.xpath("//@data-lat")[0]
        longitude = loc_dom.xpath("//@data-lng")[0]
        hours_of_operation = "<MISSING>"

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
