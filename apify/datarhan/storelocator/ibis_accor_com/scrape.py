import csv
import json
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

    DOMAIN = "accor.com"
    start_urls = [
        "https://ibis.accor.com/gb/city/hotels-london-v2352.shtml",
        "https://all.accor.com/ssr/app/ibis/hotels/united-states/index.en.shtml?dateIn=2021-01-15&nights=31&compositions=1&stayplus=false",
        "https://all.accor.com/ssr/app/ibis/hotels/canada/index.en.shtml?dateIn=2021-01-15&nights=31&compositions=1&stayplus=false&destination=Canada",
    ]

    all_locations = []
    for start_url in start_urls:
        response = session.get(start_url)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//div[@class="hotelPic"]/a/@href')
        all_locations += dom.xpath(
            '//div[@class="hotel__content hotel__block--right"]//h2/a/@href'
        )
        next_page = dom.xpath('//a[@class="sign" and contains(text(), ">")]/@href')
        while next_page:
            next_url = urljoin(start_url, next_page[0])
            response = session.get(next_url)
            dom = etree.HTML(response.text)
            all_locations += dom.xpath('//div[@class="hotelPic"]/a/@href')
            all_locations += dom.xpath(
                '//div[@class="hotel__content hotel__block--right"]//h2/a/@href'
            )
            next_page = dom.xpath('//a[@class="sign" and contains(text(), ">")]/@href')

    for url in all_locations:
        poi_url = urljoin(start_urls[0], url.split("?")[0])
        loc_response = session.get(poi_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath(
            '//script[@type="application/ld+json" and contains(text(), "telephone")]/text()'
        )
        if not poi:
            continue
        poi = json.loads(poi[0])
        add_data = loc_dom.xpath('//script[contains(text(), "hotelName")]/text()')[0]
        add_data = json.loads(add_data)

        poi_name = poi["name"]
        poi_name = poi_name if poi_name else "<MISSING>"
        street = add_data["streetAddress"]
        city = poi["address"]["addressLocality"]
        city = city if city else "<MISSING>"
        state = "<MISSING>"
        zip_code = poi["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["addressCountry"]
        country_code = country_code if country_code else "<MISSING>"
        poi_number = "<MISSING>"
        phone = poi["telephone"]
        poi_type = poi["@type"]
        latitude = loc_dom.xpath('//meta[@property="og:latitude"]/@content')[0]
        longitude = loc_dom.xpath('//meta[@property="og:longitude"]/@content')[0]
        hoo = "<MISSING>"

        item = [
            DOMAIN,
            poi_url,
            poi_name,
            street,
            city,
            state,
            zip_code,
            country_code,
            poi_number,
            phone,
            poi_type,
            latitude,
            longitude,
            hoo,
        ]
        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
