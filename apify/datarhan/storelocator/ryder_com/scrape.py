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
    session = SgRequests()

    items = []

    DOMAIN = "ryder.com"
    start_url = "https://ryder.com/locations/USA"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_state_urls = dom.xpath('//a[@class="js-grab-click js--location__link"]/@href')
    for state_url in all_state_urls:
        state_response = session.get("https://ryder.com" + state_url)
        state_dom = etree.HTML(state_response.text)
        cities_url = state_dom.xpath(
            '//a[@class="js-grab-click js--location__link location__link--cities"]/@href'
        )
        for city_url in cities_url:
            city_response = session.get("https://ryder.com" + city_url)
            city_dom = etree.HTML(city_response.text)
            locations_html = city_dom.xpath('//div[@class="location__item"]')
            for l_html in locations_html:
                store_url = "https://ryder.com" + l_html.xpath(".//a/@href")[0]
                location_name = l_html.xpath('.//h2[@itemprop="name"]/text()')[
                    -1
                ].strip()
                location_name = location_name if location_name else "<MISSING>"
                street_address = l_html.xpath(
                    './/span[@itemprop="streetAddress"]/text()'
                )
                street_address = (
                    " ".join(street_address).strip() if street_address else "<MISSING>"
                )
                city = l_html.xpath('.//span[@itemprop="addressLocality"]/text()')
                city = city[0].replace(",", "").strip() if city else "<MISSING>"
                state = l_html.xpath('.//span[@itemprop="addressRegion"]/text()')
                state = state[0].strip() if state else "<MISSING>"
                zip_code = l_html.xpath('.//span[@itemprop="postalCode"]/text()')
                zip_code = zip_code[0].strip() if zip_code else "<MISSING>"
                country_code = l_html.xpath(
                    './/span[@itemprop="addressCountry"]/text()'
                )
                country_code = country_code[0].strip() if country_code else "<MISSING>"
                store_number = store_url.split("/")[-1].strip()
                store_number = store_number if store_number else "<MISSING>"
                phone = l_html.xpath('.//span[@itemprop="telephone"]/text()')
                phone = phone[0].strip() if phone else ""
                phone = phone if phone else "<MISSING>"
                location_type = "<MISSING>"
                latitude = l_html.xpath(".//a/@data-lat")
                latitude = latitude[0] if latitude else "<MISSING>"
                longitude = l_html.xpath(".//a/@data-lng")
                longitude = longitude[0] if longitude else "<MISSING>"
                hours_of_operation = l_html.xpath(
                    './/ul[@class="location__services location__services--hours location__format--hours"]/li/text()'
                )
                hours_of_operation = (
                    " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
                )

                if state.isnumeric():
                    new_state = zip_code
                    zip_code = state
                    state = new_state

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
