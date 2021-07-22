import csv
from lxml import etree
from urllib.parse import urljoin
from w3lib.url import add_or_replace_parameter

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

    DOMAIN = "colehaan.com"
    start_url = "https://stores.colehaan.com/index.html"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }

    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)
    all_countries = dom.xpath('//a[@class="c-directory-list-content-item-link"]/@href')
    for url in all_countries:
        if "us.html" in url:
            continue
        country_url = urljoin(start_url, url)
        response = session.get(country_url)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath('//div[@class="location-list-locations-wrapper"]')
        for poi_html in all_locations:
            country_code = country_url.split("/")[-1].split(".")[0].upper()
            store_url = country_url
            own_url = poi_html.xpath(
                './/h5[@class="c-location-grid-item-title"]/a/@href'
            )
            if own_url:
                store_url = urljoin(start_url, own_url[0])
            location_name = " ".join(
                poi_html.xpath('.//h5[@class="c-location-grid-item-title"]//text()')
            )
            street_address = poi_html.xpath(
                './/span[@class="c-address-street c-address-street-1"]/text()'
            )[0]
            str_adr_2 = poi_html.xpath(
                './/span[@class="c-address-street c-address-street-2"]/text()'
            )
            if str_adr_2:
                street_address += " " + str_adr_2[0]
            city = poi_html.xpath('.//span[@class="c-address-city"]/span/text()')[0]
            if city.endswith(","):
                city = city[:-1]
            state = poi_html.xpath('.//span[@class="c-address-state"]/text()')
            state = state[0].strip() if state else "<MISSING>"
            zip_code = poi_html.xpath('.//span[@class="c-address-postal-code"]/text()')
            zip_code = zip_code[0].strip() if zip_code else "<MISSING>"
            store_number = "<MISSING>"
            phone = poi_html.xpath(
                './/div[@class="c-location-grid-item-phone"]//span/text()'
            )
            phone = phone[0] if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hoo = []
            hours_html = poi_html.xpath(".//div[@data-day-of-week-start-index]")
            if hours_html:
                days = [
                    "Sunday",
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                ]
                for i, day in enumerate(days):
                    hours = hours_html[i].xpath(".//text()")
                    hours = [e.strip() for e in hours if e.strip()]
                    hours = " ".join(hours)
                    hoo.append(f"{day} {hours}")
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
            check = f"{location_name} {street_address}"
            if check not in scraped_items:
                scraped_items.append(check)
                items.append(item)

    start_url = "https://liveapi.yext.com/v2/accounts/me/answers/vertical/query?v=20190101&api_key=c202b999eeb9609ed15439271ae840c7&jsLibVersion=v1.4.8&sessionTrackingEnabled=true&input=Open%20locations%20near%20me&experienceKey=colehaan-answers&version=PRODUCTION&filters=%7B%7D&facetFilters=%7B%7D&verticalKey=locations&limit=40&offset=0&retrieveFacets=true&locale=en"
    data = response = session.get(start_url, headers=headers).json()
    all_locations = data["response"]["results"]
    total = data["response"]["resultsCount"]
    for index in range(40, total + 40, 40):
        data = session.get(
            add_or_replace_parameter(start_url, "offset", str(index)), headers=headers
        ).json()
        all_locations += data["response"]["results"]

    for poi in all_locations:
        store_url = poi["data"]["websiteUrl"]["displayUrl"]
        location_name = poi["data"]["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["data"]["address"]["line1"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["data"]["address"]["city"]
        city = city if city else "<MISSING>"
        state = poi["data"]["address"]["region"]
        state = state if state else "<MISSING>"
        zip_code = poi["data"]["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["data"]["address"]["countryCode"]
        store_number = poi["data"]["id"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["data"]["mainPhone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["data"]["geocodedCoordinate"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["data"]["geocodedCoordinate"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        for day, hours in poi["data"]["hours"].items():
            if hours.get("openIntervals"):
                opens = hours["openIntervals"][0]["start"]
                closes = hours["openIntervals"][0]["end"]
                hours_of_operation.append(f"{day} {opens} - {closes}")
            else:
                hours_of_operation.append(f"{day} closed")
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
