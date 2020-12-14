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

    DOMAIN = "famousdaves.com"
    start_url = "https://www.famousdaves.com/Locations/Index"
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = []
    all_states = dom.xpath('//div[@id="state-list"]/a/@href')
    for state_url in all_states:
        state_response = session.get("https://www.famousdaves.com" + state_url)
        state_dom = etree.HTML(state_response.text)
        all_locations += state_dom.xpath('//div[@id="storeListContainer"]/div')

    for poi_html in all_locations:
        store_url = poi_html.xpath('.//a[@class="location-store-name"]/@href')
        store_url = store_url[0] if store_url else "<MISSING>"
        location_name = poi_html.xpath('.//a[@class="location-store-name"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi_html.xpath(
            './/div[@class="row location-store-address"]/p[1]/text()'
        )
        street_address = street_address[0] if street_address else "<MISSING>"
        city = poi_html.xpath('.//div[@class="row location-store-address"]/p[2]/text()')
        city = city[0].split(",")[0] if city else "<MISSING>"
        state = poi_html.xpath(
            './/div[@class="row location-store-address"]/p[2]/text()'
        )
        state = state[0].split(",")[-1].split()[0] if state else "<MISSING>"
        zip_code = (
            poi_html.xpath('.//div[@class="row location-store-address"]/p[2]/text()')[0]
            .split(",")[-1]
            .split()[-1]
        )
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//span[@class="location-store-phone-number"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"

        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        latitude = loc_dom.xpath('//input[@name="selectedStore.Latitude"]/@value')[0]
        longitude = loc_dom.xpath('//input[@name="selectedStore.Longitude"]/@value')[0]
        hours_of_operation = loc_dom.xpath(
            '//div[@class="row location-store-hours"]//text()'
        )
        hours_of_operation = [
            elem.strip().replace("\xa0", "")
            for elem in hours_of_operation
            if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )
        if not hours_of_operation.endswith("pm"):
            hours_of_operation = " ".join(hours_of_operation.split()[:-1])
        if "SorryFolks!" in hours_of_operation:
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
