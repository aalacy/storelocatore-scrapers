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
    items = []

    session = SgRequests()

    DOMAIN = "pizzastudiocanada.com"
    start_url = "http://pizzastudiocanada.com/home.html#locations"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_states = dom.xpath('//div[@class="column province"]')
    for state_html in all_states:
        state = state_html.xpath(".//h1/text()")[0]
        locations = state_html.xpath('.//div[@class="row"]')

        for poi_html in locations:
            store_url = "http://pizzastudiocanada.com/home.html#locations"
            location_name = poi_html.xpath(".//h2/text()")[0]
            street_address = poi_html.xpath('.//div[@class="column store"]/p/text()')[0]
            city = location_name
            zip_code = poi_html.xpath('.//div[@class="column store"]/p/text()')[-1]
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            phone = poi_html.xpath('.//a[@class="telephone fb-track-lead"]/text()')
            phone = phone[0] if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hoo = poi_html.xpath('.//table[@class="hours"]//text()')
            hoo = [elem.strip() for elem in hoo if elem.strip()]
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

            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
