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

    DOMAIN = "cashstore.com"
    start_url = "https://www.cashstore.com/components/getlocations"
    formdata = {
        "lat": "42.5896728",
        "lng": "-89.6628111",
        "pageSize": "500",
        "page": "0",
        "radius": "50000",
        "useIcons": "true",
    }

    headers = {
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    response = session.post(start_url, data=formdata, headers=headers)
    dom = etree.HTML(response.text)

    all_poi_html = dom.xpath('//div[@class="media location location_box"]')
    for poi_html in all_poi_html:
        store_url = ""
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi_html.xpath('.//h4[@class="media-heading"]/text()')
        location_name = location_name[-1].strip() if location_name else "<MISSING>"
        street_address = poi_html.xpath('.//span[@class="locAddr1"]/text()')[0]
        street_address_2 = poi_html.xpath('.//span[@class="locAddr2"]/text()')
        if street_address_2:
            street_address += ", " + street_address_2[0]
        street_address = street_address if street_address else "<MISSING>"
        city = poi_html.xpath('.//span[@class="locCityStSip"]/text()')
        city = city[0].split(",")[0] if city else "<MISSING>"
        state = poi_html.xpath('.//span[@class="locCityStSip"]/text()')
        state = state[0].split(",")[-1].strip().split()[0] if state else "<MISSING>"
        zip_code = poi_html.xpath('.//span[@class="locCityStSip"]/text()')
        zip_code = (
            zip_code[0].split(",")[-1].strip().split()[-1] if zip_code else "<MISSING>"
        )
        country_code = ""
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = ""
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi_html.xpath("@data-latitude")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = poi_html.xpath("@data-longitude")
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = poi_html.xpath(
            './/p[strong[contains(text(), "Hours:")]]/text()'
        )
        hours_of_operation = (
            hours_of_operation[1] if hours_of_operation else "<MISSING>"
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
