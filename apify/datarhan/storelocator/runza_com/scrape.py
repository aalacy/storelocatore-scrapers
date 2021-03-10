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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    DOMAIN = "runza.com"
    start_url = "https://www.runza.com/locations/search"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }

    all_locations = []
    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)
    all_states = dom.xpath('//select[@id="state"]/option/@value')[1:]
    for state in all_states:
        state_url = "https://www.runza.com/locations/search?state={}&city=&distance=&postal_code=&submit=Search"
        response = session.get(state_url.format(state))
        dom = etree.HTML(response.text)
        all_locations += dom.xpath("//div[@itemscope]")
        next_page = dom.xpath('//span[@class="next control"]/a/@href')
        while next_page:
            response = session.get(urljoin(start_url, next_page[0]))
            dom = etree.HTML(response.text)
            all_locations += dom.xpath("//div[@itemscope]")
            next_page = dom.xpath('//span[@class="next control"]/a/@href')

    for poi_html in all_locations:
        store_url = "<MISSING>"
        location_name = poi_html.xpath('.//h2[@itemprop="name"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi_html.xpath('.//div[@class="street-address"]/text()')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = poi_html.xpath('.//span[@itemprop="addressLocality"]/text()')
        city = city[0] if city else "<MISSING>"
        state = poi_html.xpath('.//span[@itemprop="addressRegion"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = poi_html.xpath('.//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//div[@itemprop="telephone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = poi_html.xpath("@itemtype")[0].split("/")[-1]
        if location_type != "FastFoodRestaurant":
            continue
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = poi_html.xpath('.//div[@itemprop="openingHours"]//text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()][1:]
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
