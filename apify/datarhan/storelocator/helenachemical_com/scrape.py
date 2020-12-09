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

    DOMAIN = "helenaagri.com"
    start_url = "https://helenaagri.com/locations/"
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    states = dom.xpath('//select[@name="state"]/option/@value')
    for state in states:
        state_url = "https://helenaagri.com/locations/?zip=&city=&state={}".format(
            state
        )
        state_response = session.get(state_url)
        dom = etree.HTML(state_response.text)
        all_locations = dom.xpath('//li[@class="locations-list-container"]')
        for loc_html in all_locations:
            store_url = "<MISSING>"
            location_name = loc_html.xpath('.//li[@class="locations-name"]/text()')
            location_name = location_name[-1].strip() if location_name else "<MISSING>"
            street_address = loc_html.xpath('.//span[@class="add-1"]/text()')
            street_address = street_address[0] if street_address else "<MISSING>"
            city = loc_html.xpath('.//span[@class="add-3"]/text()')[0].split(",")[0]
            city = city if city else "<MISSING>"
            state = (
                loc_html.xpath('.//span[@class="add-3"]/text()')[0]
                .split(",")[-1]
                .strip()
                .split()[0]
            )
            state = state if state else "<MISSING>"
            zip_code = (
                loc_html.xpath('.//span[@class="add-3"]/text()')[0]
                .split(",")[-1]
                .strip()
                .split()[-1]
            )
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            phone = loc_html.xpath('.//li[@class="locations-phone"]/a/text()')
            phone = phone[0] if phone else "<MISSING>"
            if "orange" in loc_html.xpath('.//img[@class="marker-image"]/@src')[0]:
                location_type = "Wholesale/Retail"
            if "blue" in loc_html.xpath('.//img[@class="marker-image"]/@src')[0]:
                location_type = "Retail"
            else:
                location_type = "Wholesale"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
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
