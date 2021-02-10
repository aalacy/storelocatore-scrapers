import csv
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgpostal import International_Parser, parse_address


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

    DOMAIN = "orkincanada.ca"
    start_url = "https://www.orkincanada.ca/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="card card--location"]/a[h3]/@href')
    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//div[@class="card card--location"]/h3/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath('//div[@class="card--divider"]/p/text()')
        raw_address = [elem for elem in raw_address if "Week" not in elem]
        raw_address = " ".join(raw_address)
        adr = parse_address(raw_address, International_Parser())
        street_address = adr.street_address_1
        if adr.street_address_2:
            street_address = adr.street_address_2 + " " + street_address
        city = adr.city
        state = adr.state
        zip_code = adr.postcode
        country_code = adr.country
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//span[@class="card__phone"]/text()')
        phone = phone[0].split(": ")[-1] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = loc_dom.xpath('//div[@class="card--divider"]/p/text()')
        hoo = [elem for elem in hoo if "Week" in elem]
        hours_of_operation = " ".join(hoo).replace("\n", "")

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
