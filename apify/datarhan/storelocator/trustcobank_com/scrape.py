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

    DOMAIN = "trustcobank.com"
    start_url = "https://www.trustcobank.com/branch-and-atm-locator.php"

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }
    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//select[@name="branch"]/option/@value')

    for store_number in all_locations[1:]:
        store_url = "https://www.trustcobank.com/branch-and-atm-locator.php?zip_code=&search=&distance=10&branch={}#search".format(
            store_number
        )
        location_response = session.get(store_url, headers=headers)
        loc_dom = etree.HTML(location_response.text)

        location_name = loc_dom.xpath('//div[@id="main"]/h1/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        address_raw = loc_dom.xpath('//div[@id="location-info"]/p/text()')
        address_raw = [elem.strip() for elem in address_raw if elem.strip()]
        street_address = address_raw[0]
        street_address = street_address if street_address else "<MISSING>"
        city = address_raw[1].split(",")[0]
        state = address_raw[1].split(",")[-1].split()[0]
        zip_code = address_raw[1].split(",")[-1].split()[-1]
        country_code = "<MISSING>"
        phone = loc_dom.xpath(
            '//h2[contains(text(), "Phone Number")]/following-sibling::p/text()'
        )
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = loc_dom.xpath(
            '//table[@class="table-location table-hours"]//text()'
        )
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
