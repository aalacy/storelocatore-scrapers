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

    DOMAIN = "jaguar.co.uk"
    start_url = "https://www.jaguar.co.uk/national-dealer-locator.html?radius=100&placeName={}&filter=All"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36"
    }

    response = session.get(
        "https://www.britannica.com/topic/list-of-cities-and-towns-in-the-United-Kingdom-2034188"
    )
    dom = etree.HTML(response.text)
    cities = dom.xpath("//section/h2/a/text()")

    for city in cities:
        response = session.get(start_url.format(city), headers=hdr)
        dom = etree.HTML(response.text)

        all_poi_html = dom.xpath('//div[@class="infoCardDealer infoCard"]')
        for poi_html in all_poi_html:
            store_url = poi_html.xpath('.//div[@class="dealerWebsiteDiv"]//a/@href')
            store_url = store_url[0] if store_url else "<MISSING>"
            location_name = poi_html.xpath(
                './/span[@class="dealerNameText fontBodyCopyLarge"]/text()'
            )
            location_name = location_name[0] if location_name else "<MISSING>"
            address_raw = poi_html.xpath('.//span[@class="addressText"]/text()')[
                0
            ].split(",")
            if len(address_raw) == 5:
                street_address = ", ".join(address_raw[:2])
                city = address_raw[2]
                state = address_raw[3]
                zip_code = address_raw[-1]
            if len(address_raw) == 4:
                street_address = address_raw[0]
                city = address_raw[1]
                state = address_raw[2]
                zip_code = address_raw[-1]
            if len(address_raw) == 3:
                street_address = address_raw[0]
                city = address_raw[1]
                state = "<MISSING>"
                zip_code = address_raw[-1]
            city = city.strip() if city else "<MISSING>"
            country_code = "<MISSING>"
            country_code = country_code if country_code else "<MISSING>"
            store_number = poi_html.xpath("@data-ci-code")
            store_number = store_number[0] if store_number else "<MISSING>"
            phone = poi_html.xpath('.//span[@class="phoneNumber"]/a/text()')
            phone = phone[0] if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = poi_html.xpath("@data-lat")
            latitude = latitude[0] if latitude else "<MISSING>"
            longitude = poi_html.xpath("@data-lng")
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

            if store_number not in scraped_items:
                scraped_items.append(store_number)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
