import csv
from lxml import etree
from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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

    DOMAIN = "expressoil.com"
    start_url = "https://www.expressoil.com/stores/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="location-store"]')

    for poi_html in all_locations:
        store_url = poi_html.xpath("@data-viewurl")
        store_url = store_url[0] if store_url else "<MISSING>"
        location_name = poi_html.xpath('.//div[@class="location-details"]/a/text()')
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi_html.xpath('.//div[@class="location-details"]/p[1]/text()')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = poi_html.xpath("@data-city")
        city = city[0] if city else "<MISSING>"
        state = poi_html.xpath('.//div[@class="location-details"]/p[1]/text()')
        state = state[-1].split(",")[-1].strip().split()[0] if state else "<MISSING>"
        zip_code = poi_html.xpath('.//div[@class="location-details"]/p[1]/text()')
        zip_code = (
            zip_code[-1].split(",")[-1].strip().split()[-1] if zip_code else "<MISSING>"
        )
        country_code = "<MISSING>"
        store_number = poi_html.xpath('.//div[@class="location-cta"]/a/@href')
        store_number = store_number[0].split("=")[-1] if store_number else "<MISSING>"
        if "/" in store_number:
            store_number = store_number.split("/")[-2]
        store_response = session.get(store_url)
        store_dom = etree.HTML(store_response.text)
        phone = store_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi_html.xpath("@data-latitude")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = poi_html.xpath("@data-longitude")
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = store_dom.xpath('//h5[span[@clas="location-hrs"]]//text()')
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation[1:]) if hours_of_operation else "<MISSING>"
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


hdr = {
    "authority": "www.ediblearrangements.com",
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
    "content-type": "application/json; charset=UTF-8",
    "origin": "https://www.ediblearrangements.com",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}
