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

    DOMAIN = "bibibop.com"
    start_url = "https://bibibop.com/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//span[@class="location-info"]/a/@href')

    for store_url in list(set(all_locations)):
        if "menu" in store_url:
            continue
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//div[@id="single-location-body"]//h1/text()')[
            0
        ].strip()
        raw_address = loc_dom.xpath('//p[@class="address-container"]/text()')
        raw_address = [e.strip() for e in raw_address]
        street_address = raw_address[0]
        city = raw_address[1].split(", ")[0]
        state = raw_address[1].split(", ")[-1].split()[0]
        zip_code = raw_address[1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//p[@class="telephone"]/a/text()')[0]
        location_type = "<MISSING>"
        latitude = loc_dom.xpath("//@data-latitude")[0]
        longitude = loc_dom.xpath("//@data-longitude")[0]
        hoo = loc_dom.xpath(
            '//div[@class="tabs-panel is-active"]//tbody[tr[@class="today"]]//text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        if store_url == "<MISSING>":
            location_type = "coming soon"
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
