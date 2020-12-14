import csv
import json
from lxml import etree

from sgrequests import SgRequests
from sgselenium import SgFirefox


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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []

    DOMAIN = "daveandbusters.com"
    start_url = "https://www.daveandbusters.com/locations"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="location-list-item"]//a/@href')
    for url in list(set(all_locations)):
        store_url = "https://www.daveandbusters.com" + url
        response = session.get(store_url, headers=hdr)
        dom = etree.HTML(response.text)
        poi = dom.xpath('//script[@type="application/ld+json"]/text()')
        if poi:
            poi = json.loads(poi[0])
            location_name = poi["name"]
            street_address = poi["address"]["streetAddress"]
            city = poi["address"]["addressLocality"]
            state = poi["address"].get("addressRegion")
            state = state if state else "<MISSING>"
            zip_code = poi["address"]["postalCode"]
            country_code = poi["address"]["addressCountry"]
            store_number = "<MISSING>"
            phone = poi.get("telephone")
            phone = phone if phone else "<MISSING>"
            location_type = poi["@type"]
            latitude = poi["geo"]["latitude"]
            longitude = poi["geo"]["longitude"]
            hours_of_operation = []
            for elem in poi["openingHoursSpecification"]:
                for day in elem["dayOfWeek"]:
                    hours_of_operation.append(
                        f'{day} {elem["opens"]} - {elem["closes"]}'
                    )
            hours_of_operation = (
                " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
            )
        else:
            with SgFirefox() as driver:
                driver.get("https://www.daveandbusters.com/locations/memphis")
                driver_r = etree.HTML(driver.page_source)
            location_name = driver_r.xpath(
                '//div[@class="dave-busters-header"]//text()'
            )
            location_name = (
                " ".join([elem.strip() for elem in location_name])
                if location_name
                else "<MISSING>"
            )
            street_address = driver_r.xpath(
                '//div[@class="location-address ng-binding"]/text()'
            )[0].strip()
            city = driver_r.xpath(
                '//div[@class="location-address-2 ng-binding"]/text()'
            )[0].split(",")[0]
            state = driver_r.xpath(
                '//div[@class="location-address-2 ng-binding"]/text()'
            )[0].split(",")[1]
            state = state if state else "<MISSING>"
            zip_code = driver_r.xpath(
                '//div[@class="location-address-2 ng-binding"]/text()'
            )[0].split(",")[-1]
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            phone = driver_r.xpath('//div[@class="location-phone"]/a/text()')
            phone = "".join(phone).strip() if phone else "<MISSING>"
            location_type = "<MISSING>"
            geo = (
                driver_r.xpath('//a[contains(@href, "google.com/maps")]/@href')[0]
                .split("=")[1]
                .split("&")[0]
            )
            latitude = geo.split(",")[0]
            longitude = geo.split(",")[-1]
            hours_of_operation = driver_r.xpath(
                '//div[@class="location-hours"]//text()'
            )
            hours_of_operation = [
                elem.strip() for elem in hours_of_operation if elem.strip()
            ]
            hours_of_operation = (
                " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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
