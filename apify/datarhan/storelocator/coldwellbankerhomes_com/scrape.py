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
    scraped_items = []

    DOMAIN = "coldwellbankerhomes.com"
    start_url = "https://www.coldwellbankerhomes.com/sitemap/offices/"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }
    all_poi_urls = []
    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)
    all_states_urls = dom.xpath('//tbody[@class="notranslate"]//td/a/@href')
    for url in all_states_urls:
        state_response = session.get(
            "https://www.coldwellbankerhomes.com" + url, headers=headers
        )
        state_dom = etree.HTML(state_response.text)
        all_cities_urls = state_dom.xpath('//tbody[@class="notranslate"]//td/a/@href')
        for city_url in all_cities_urls:
            city_response = session.get(
                "https://www.coldwellbankerhomes.com" + city_url, headers=headers
            )
            city_dom = etree.HTML(city_response.text)
            poi_urls = city_dom.xpath("//div[@itemscope]/p/a/@href")
            poi_urls = [elem for elem in poi_urls if elem != "#"]
            all_poi_urls += poi_urls

    for poi_url in list(set(all_poi_urls)):
        store_url = "https://www.coldwellbankerhomes.com" + poi_url
        poi_response = session.get(store_url)
        poi_dom = etree.HTML(poi_response.text)
        location_name = poi_dom.xpath('//h1[@itemprop="name"]/span/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi_dom.xpath('//span[@itemprop="streetAddress"]/text()')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = poi_dom.xpath('//span[@itemprop="addressLocality"]/text()')
        city = city[0] if city else "<MISSING>"
        state = poi_dom.xpath('//span[@itemprop="addressRegion"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = poi_dom.xpath('//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[0].strip() if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi_dom.xpath("//@data-officeid")
        store_number = store_number[0] if store_number else "<MISSING>"
        phone = poi_dom.xpath(
            '//span[@itemprop="telephone"]/a[@class="phone-link"]/text()'
        )
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi_dom.xpath('//meta[@itemprop="latitude"]/@content')
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = poi_dom.xpath('//meta[@itemprop="longitude"]/@content')
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = "<MISSING>"

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

        check = "{} {}".format(location_name, street_address)
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
