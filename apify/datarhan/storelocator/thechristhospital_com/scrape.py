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

    DOMAIN = "thechristhospital.com"
    start_url = "https://www.thechristhospital.com/"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }

    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)

    all_locations = []
    dir_urls = dom.xpath('//a[@href="/locations"]/following-sibling::div/ul/li/a/@href')
    for url in dir_urls:
        dir_response = session.get("https://www.thechristhospital.com" + url)
        dir_dom = etree.HTML(dir_response.text)
        all_locations += dir_dom.xpath('//div[@class="location js-location"]')

    for poi_html in list(set(all_locations)):
        store_url = poi_html.xpath(
            './/a[@class="location-header js-location__name"]/@href'
        )
        store_url = store_url[0] if store_url else "<MISSING>"
        location_name = poi_html.xpath(
            './/a[@class="location-header js-location__name"]/text()'
        )
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi_html.xpath('.//span[@class="addressline"]/text()')
        street_address = street_address[0].strip() if street_address else "<MISSING>"
        address_2 = poi_html.xpath('.//span[@class="addressline addressline2"]/text()')
        if address_2:
            street_address += ", " + address_2[0].strip()
        city = poi_html.xpath('.//span[@class="addressline"]/text()')
        city = city[-1].strip().split(",")[0] if city else "<MISSING>"
        state = poi_html.xpath('.//span[@class="addressline"]/text()')
        state = state[-1].strip().split(",")[-1].split()[0] if state else "<MISSING>"
        zip_code = poi_html.xpath('.//span[@class="addressline"]/text()')
        zip_code = (
            zip_code[-1].strip().split(",")[-1].split()[-1] if zip_code else "<MISSING>"
        )
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//span[@class="phonenumber"]//b/text()')
        phone = phone[0].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = poi_html.xpath('.//div[@class="hours"]//text()')
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        if hours_of_operation == ["Hours"]:
            hours_of_operation = ""
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
