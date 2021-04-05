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
    session = SgRequests()

    items = []

    DOMAIN = "1800flowers.com"
    start_url = "https://florist.1800flowers.com/"

    all_locations = []
    all_states = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DC",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]
    for state in all_states:
        state_url = "https://florist.1800flowers.com/us-{}".format(state)
        state_response = session.get(state_url)
        state_dom = etree.HTML(state_response.text)
        all_locations += state_dom.xpath('//td[@class="listAddress"]/a/@href')

    for url in all_locations:
        store_url = urljoin(start_url, url)
        store_response = session.get(store_url)
        store_dom = etree.HTML(store_response.text)

        store_url = store_url if store_url else "<MISSING>"
        location_name = store_dom.xpath('//div[@class="storeinfo"]/h1/text()')
        if not location_name:
            continue
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = store_dom.xpath('//span[@itemprop="streetAddress"]/text()')
        street_address = street_address[0].strip() if street_address else "<MISSING>"
        city = store_dom.xpath('//span[@itemprop="addressLocality"]/text()')
        city = city[0] if city else "<MISSING>"
        state = store_dom.xpath('//span[@itemprop="addressRegion"]/text()')
        state = state[0].strip() if state else "<MISSING>"
        zip_code = store_dom.xpath('//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[0].strip() if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = store_dom.xpath('//span[@itemprop="telephone"]/text()')
        phone = phone[0].split("Fax:")[0].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = store_dom.xpath('//meta[@itemprop="latitude"]/@content')
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = store_dom.xpath('//meta[@itemprop="longitude"]/@content')
        longitude = longitude[0] if longitude else "<MISSING>"

        days = store_dom.xpath('//table[@class="hourstbl"]//th/text()')
        hours = []
        hours_raw = store_dom.xpath('//table[@class="hourstbl"]//tr/td')
        for elem in hours_raw:
            hours_text = elem.xpath(".//text()")
            hours_text = " ".join([elem.strip() for elem in hours_text])
            hours.append(hours_text)
        hours_of_operation = " ".join(list(map(lambda d, h: d + " " + h, days, hours)))

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
