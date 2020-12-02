import csv
import json
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

    DOMAIN = "postnet.com"

    states = [
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

    start_url = "https://locations.postnet.com/search?q={}"

    for state in states:
        response = session.get(start_url.format(state))
        dom = etree.HTML(response.text)

        all_urls = dom.xpath(
            '//ol[@class="ResultList"]/li//a[@class="Teaser-titleLink"]/@href'
        )
        for url in all_urls:
            store_url = "https://locations.postnet.com/" + url
            store_response = session.get(store_url)
            store_dom = etree.HTML(store_response.text)

            location_name = " ".join(store_dom.xpath(".//h1//text()"))
            location_name = location_name if location_name else "<MISSING>"
            street_address = store_dom.xpath(
                '//meta[@itemprop="streetAddress"]/@content'
            )
            street_address = street_address[0] if street_address else "<MISSING>"
            city = store_dom.xpath('//meta[@itemprop="addressLocality"]/@content')
            city = city[0] if city else "<MISSING>"
            state = store_dom.xpath('//abbr[@itemprop="addressRegion"]/text()')
            state = state[0] if state else "<MISSING>"
            zip_code = store_dom.xpath('//span[@itemprop="postalCode"]/text()')
            zip_code = zip_code[0] if zip_code else "<MISSING>"
            country_code = store_dom.xpath("//address/@data-country")
            country_code = country_code[0] if country_code else "<MISSING>"
            store_number = ""
            store_number = store_number if store_number else "<MISSING>"
            phone = store_dom.xpath('//span[@itemprop="telephone"]/text()')
            phone = phone[0] if phone else "<MISSING>"
            location_type = ""
            location_type = location_type if location_type else "<MISSING>"
            latitude = store_dom.xpath('//meta[@itemprop="latitude"]/@content')
            latitude = latitude[0] if latitude else "<MISSING>"
            longitude = store_dom.xpath('//meta[@itemprop="longitude"]/@content')
            longitude = longitude[0] if longitude else "<MISSING>"
            hours_of_operation = []
            hours = store_dom.xpath("//div/@data-days")[0]
            hours = json.loads(hours)
            for elem in hours:
                if elem["intervals"]:
                    end = str(elem["intervals"][0]["end"])[:2] + ":00"
                    start = str(elem["intervals"][0]["start"])[:2] + ":00"
                    hours_of_operation.append(
                        "{} {} - {}".format(elem["day"], start, end)
                    )
                else:
                    hours_of_operation.append("{}  closed".format(elem["day"]))
            hours_of_operation = (
                ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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

            if location_name not in scraped_items:
                scraped_items.append(location_name)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
