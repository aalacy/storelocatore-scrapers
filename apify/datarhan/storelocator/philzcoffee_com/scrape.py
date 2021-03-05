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

    DOMAIN = "philzcoffee.com"
    start_url = "https://www.philzcoffee.com/locations"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }

    response = session.post(start_url, headers=headers)
    dom = etree.HTML(response.text)

    all_poi = dom.xpath('//div[contains(@id, "modal-")]')
    for poi_html in all_poi:
        store_url = "<MISSING>"
        location_name = poi_html.xpath(
            './/h1[@class="modal-title location-title"]/text()'
        )
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath('.//div[@class="location-text text-left"]/text()')
        raw_address = [elem.strip() for elem in raw_address]
        if not raw_address:
            continue
        street_address = raw_address[0]
        city = raw_address[-1].split(",")[0]
        state = raw_address[-1].split(",")[-1].split()[0]
        if state.isdigit():
            state = raw_address[-1].split(",")[-2].split()[0]
        zip_code = raw_address[-1].split(",")[-1].split()[-1]
        zip_code = zip_code if zip_code else "<MISSING>"
        if "Instagram" in zip_code:
            continue
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath(
            './/div[@class="pull-left location-phone-detail"]/div[2]/text()'
        )
        phone = phone[0].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = poi_html.xpath(
            './/div[@class="pull-right location-text div-get-directions"]/a[contains(@href, "/maps/")]/@href'
        )
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if geo:
            if "@" in geo:
                geo = geo[0].split("@")[-1].split(",")[:2]
                latitude = geo[0]
                longitude = geo[1]
        hours_of_operation = poi_html.xpath(
            './/div[@class="pull-right pull-right-locations-mobile"]/div[2]/text()'
        )
        hours_of_operation = (
            "".join(hours_of_operation).strip() if hours_of_operation else "<MISSING>"
        )
        if "CLOSED" in hours_of_operation:
            location_type = "closed"

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
