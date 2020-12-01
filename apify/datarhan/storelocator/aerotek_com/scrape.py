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

    DOMAIN = "aerotek.com"
    start_urls = [
        "https://www.aerotek.com/en-ca/locations/canada",
        "https://aerotek.com/en/locations/united-states",
    ]

    for url in start_urls:
        response = session.get(url)
        dom = etree.HTML(response.text)
        country_urls = dom.xpath('//div[@id="location-title"]/a/@href')
        for poi_url in country_urls:
            store_url = "https://aerotek.com" + poi_url
            strore_response = session.get(store_url)
            store_dom = etree.HTML(strore_response.text)

            location_name = store_dom.xpath('//div[@id="location-title"]/a/text()')[0]
            location_name = location_name if location_name else "<MISSING>"
            street_address = store_dom.xpath(
                '//span[@class="acs-location-address"]/text()'
            )[0]
            street_address_2 = store_dom.xpath(
                '//spa[@class="acs-location-address2"]/text()'
            )
            if street_address_2:
                street_address += ", " + street_address_2
            street_address = street_address if street_address else "<MISSING>"
            city = store_dom.xpath('//span[@class="acs-city"]/text()')[0].split(",")[0]
            city = city if city else "<MISSING>"
            state = (
                store_dom.xpath('//span[@class="acs-city"]/text()')[0]
                .split(",")[-1]
                .strip()
                .split()[:-1]
            )
            state = " ".join(state) if state else "<MISSING>"
            zip_code = (
                store_dom.xpath('//span[@class="acs-city"]/text()')[0]
                .split(",")[-1]
                .strip()
                .split()[1:]
            )
            zip_code = " ".join(zip_code) if zip_code else "<MISSING>"
            country_code = store_dom.xpath('//span[@class="acs-country"]/text()')[0]
            country_code = country_code if country_code else "<MISSING>"
            store_number = ""
            store_number = store_number if store_number else "<MISSING>"
            phone = store_dom.xpath('//span[@class="acs-location-phone"]/a/text()')[0]
            phone = phone if phone else "<MISSING>"
            location_type = ""
            location_type = location_type if location_type else "<MISSING>"

            store_data = store_dom.xpath(
                '//*[contains(@data-ux-args, "Lat")]/@data-ux-args'
            )
            if store_data:
                store_data = json.loads(store_data[0])
                latitude = store_data["MapPoints"][0]["Lat"]
                longitude = store_data["MapPoints"][0]["Long"]
            else:
                latitude = store_dom.xpath(
                    '//div[@id="location-title"]/@data-mappoint'
                )[0].split(",")[0]
                longitude = store_dom.xpath(
                    '//div[@id="location-title"]/@data-mappoint'
                )[0].split(",")[1]
            latitude = latitude if latitude else "<MISSING>"
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = store_dom.xpath(
                '//div[@class="score-content-spot aerotek-location-hours"]//text()'
            )
            hours_of_operation = [
                elem.strip() for elem in hours_of_operation if elem.strip()
            ]
            hours_of_operation = (
                ", ".join(hours_of_operation).replace("Office Hours:,", "").strip()
            )
            hours_of_operation = (
                hours_of_operation if hours_of_operation else "<MISSING>"
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

            if street_address not in scraped_items:
                scraped_items.append(street_address)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
