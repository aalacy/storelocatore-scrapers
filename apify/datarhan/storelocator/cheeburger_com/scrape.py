import csv
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_usa


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

    DOMAIN = "cheeburger.com"
    start_url = "https://www.cheeburger.com/locations/#usa-locations"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    }

    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@class="vc_toggle vc_toggle_default vc_toggle_color_default vc_toggle_size_md"]'
    )
    for poi_html in all_locations:
        store_url = "<MISSING>"
        location_name = poi_html.xpath('.//div[@class="vc_toggle_title"]/h4/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi_html.xpath('.//div[@class="address"]/h5/text()')
        street_address = (
            " ".join([e for e in street_address[:2] if "Phone" not in e])
            if street_address
            else "<MISSING>"
        )
        raw_adr = f"{location_name} {street_address}"
        addr = parse_address_usa(raw_adr)
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address = addr.street_address_2 + " " + addr.street_address_1
        if " Tx " in street_address:
            street_address = street_address.split(" Tx ")[-1]
        city = poi_html.xpath('.//div[@class="vc_toggle_title"]/h4/text()')[0].split(
            " - "
        )[0]
        state = poi_html.xpath('.//div[@class="vc_toggle_title"]/h4/text()')[0].split(
            " - "
        )[-1]
        country_code = "USA"
        store_number = "<MISSING>"
        phone = [
            e
            for e in poi_html.xpath('.//div[@class="address"]/h5/text()')
            if "Phone" in e
        ]
        phone = phone[0].split()[-1] if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = poi_html.xpath('.//a[contains(@href, "/@")]/@href')
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if geo:
            geo = geo[-1].split("/@")[-1].split(",")[:2]
            latitude = geo[0]
            longitude = geo[1]
        hoo = poi_html.xpath('.//h5[@class="hours"]/following-sibling::h5/text()')
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
