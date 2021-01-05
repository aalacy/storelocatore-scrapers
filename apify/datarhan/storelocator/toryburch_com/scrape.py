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
    items = []

    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    DOMAIN = "toryburch.com"
    start_url = "https://www.toryburch.com/stores?country=US"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }
    response = session.get(start_url, headers=headers)

    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@itemtype="http://schema.org/ClothingStore"]')

    for poi_html in all_locations:
        store_url = poi_html.xpath('.//meta[@itemprop="url"]/@content')
        store_url = store_url[0] if store_url else "<MISSING>"
        location_name = poi_html.xpath('.//p[@class="store-name"]/a/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi_html.xpath('.//meta[@itemprop="streetAddress"]/@content')[
            0
        ]
        if len(street_address.split(",")) == 3:
            street_address = ", ".join(street_address.split(",")[1:])
        city = poi_html.xpath('.//meta[@itemprop="addressLocality"]/@content')
        city = city[0] if city else "<MISSING>"
        if "null" in city:
            city = "<MISSING>"
        state = poi_html.xpath('.//meta[@itemprop="addressRegion"]/@content')[0]
        zip_code = poi_html.xpath('.//meta[@itemprop="postalCode"]/@content')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = poi_html.xpath('.//meta[@itemprop="addressCountry"]/@content')
        country_code = country_code[0] if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//p[@itemprop="telephone"]/a/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = poi_html.xpath("@itemtype")[0].split("/")[-1]

        loc_response = session.get(store_url, headers=headers)
        loc_dom = etree.HTML(loc_response.text)
        latitude = loc_dom.xpath('//meta[@itemprop="latitude"]/@content')
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = loc_dom.xpath('//meta[@itemprop="longitude"]/@content')
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = poi_html.xpath('.//div[@class="store-hours-info"]//text()')
        hours_of_operation = (
            " ".join(hours_of_operation).replace("\n", " ")
            if hours_of_operation
            else "<MISSING>"
        )

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
