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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []
    scraped_items = []

    DOMAIN = "loumalnatis.com"
    start_urls = [
        "https://www.loumalnatis.com/chicagoland",
        "https://www.loumalnatis.com/arizona",
        "https://www.loumalnatis.com/wisconsin",
        "https://www.loumalnatis.com/indiana",
    ]

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }
    for start_url in start_urls:
        response = session.get(start_url, headers=headers)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath('//div[@id="locatorMapList"]/div')

        for poi_html in all_locations:
            store_url = poi_html.xpath(
                './/div[@class="sideBar_MapAddressElement sideBar_MapMoreDetails"]/a/@href'
            )
            store_url = store_url[0] if store_url else "<MISSING>"
            loc_response = session.get(store_url, headers=headers)
            loc_dom = etree.HTML(loc_response.text)

            location_name = poi_html.xpath(
                './/div[@class="sideBar_MapAddressElementClickable desktop-only"]/text()'
            )
            location_name = location_name[0] if location_name else "<MISSING"
            street_address = loc_dom.xpath('//span[@itemprop="streetAddress"]/text()')
            street_address = street_address[0] if street_address else "<MISSING>"
            city = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')
            city = city[0] if city else "<MISSING>"
            state = loc_dom.xpath('//span[@itemprop="addressRegion"]/text()')
            state = state[0] if state else "<MISSING>"
            zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')
            zip_code = zip_code[0] if zip_code else "<MISSING>"
            country_code = "<MISSING>"
            location_type = loc_dom.xpath('//div[@id="contentArea"]/span/@itemtype')[
                0
            ].split("/")[-1]
            if "Coming" in location_name:
                location_type = "coming soon"
            store_number = "<MISSING>"
            phone = loc_dom.xpath('//label[@itemprop="telephone"]/text()')
            phone = phone[0] if phone else "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours_of_operation = loc_dom.xpath(
                '//h5[contains(text(), "Location Hours:")]/following-sibling::p[1]//text()'
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
            check = f"{location_name} {street_address}"
            if check not in scraped_items:
                scraped_items.append(check)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
