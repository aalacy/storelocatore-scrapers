import csv
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl


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

    DOMAIN = "boyersfood.com"
    start_url = "https://www.boyersfood.com/store-locator.php"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="row locations"]/div')

    for poi_html in all_locations:
        store_url = "https://www.boyersfood.com/store-locator.php"
        location_name = poi_html.xpath(".//@name")
        location_name = location_name[0] if location_name else "<MISSING>"
        if "Coming Soon" in location_name:
            continue
        raw_address = poi_html.xpath('.//div[@class="col-xs-9 col-sm-8"]/p/text()')
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        if len(raw_address) != 5:
            raw_address = [" ".join(raw_address[:2])] + raw_address[2:]
        addr = parse_address_intl(" ".join(raw_address[:2]))
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = raw_address[2]
        location_type = "<MISSING>"
        geo = (
            poi_html.xpath('.//a[@target="_blank"]/@href')[0]
            .split("/@")[-1]
            .split(",")[:2]
        )
        latitude = geo[0]
        longitude = geo[1]
        if len(raw_address) > 3:
            hours_of_operation = raw_address[3]
        else:
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
