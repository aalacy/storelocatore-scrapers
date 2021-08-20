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

    DOMAIN = "biscuitscafe.com"
    start_urls = [
        "https://www.biscuitscafe.com/arizona/",
        "https://www.biscuitscafe.com/oregon/",
        "https://www.biscuitscafe.com/washington/",
    ]

    all_locations = []
    for start_url in start_urls:
        response = session.get(start_url)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//div[@data-vc-content=".vc_tta-panel-body"]')

    for poi_html in all_locations:
        store_url = "<MISSING>"
        location_name = poi_html.xpath('.//span[@class="vc_tta-title-text"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi_html.xpath('.//div[@class="wpb_wrapper"]/*[1]/text()')
        if not street_address:
            street_address = poi_html.xpath('.//div[@class="wpb_wrapper"]/p[2]/text()')
        street_address = (
            street_address[0]
            if street_address and street_address[0].strip()
            else "<MISSING>"
        )
        if street_address == "<MISSING>":
            if "3rd and Bell Street" in location_name:
                street_address = "310 E Bell Rd"
            elif "Thunderbird & 101" in location_name:
                street_address = "8877 W Thunderbird Rd"
        raw_address = poi_html.xpath('.//div[@class="wpb_wrapper"]//text()')
        if not raw_address:
            raw_address = poi_html.xpath('.//div[@class="wpb_wrapper"]/*[2]/text()')
        raw = " ".join([elem.strip() for elem in raw_address[:4] if elem.strip()])
        parsed_addr = parse_address_usa(raw)
        city = parsed_addr.city
        if not city:
            city = poi_html.xpath('.//div[@style="text-align: center;"]/strong/text()')
            city = city[-1].split(",")[0] if city else ""
        if not city:
            city = (
                poi_html.xpath('.//p[@style="text-align: center;"]/text()')[-1]
                .split(", ")[0]
                .strip()
            )
        city = city if city else "<MISSING>"
        state = parsed_addr.state
        if not state:
            state = poi_html.xpath('.//div[@style="text-align: center;"]/strong/text()')
            state = state[-1].split(",")[-1].split()[0] if state else ""
        if not state:
            state = (
                poi_html.xpath('.//p[@style="text-align: center;"]/text()')[-1]
                .split(", ")[-1]
                .split()[0]
            )
        state = state if state else "<MISSING>"
        zip_code = parsed_addr.postcode
        if not zip_code:
            zip_code = poi_html.xpath(
                './/div[@style="text-align: center;"]/strong/text()'
            )
            zip_code = zip_code[-1].split(",")[-1].split()[-1] if zip_code else ""
        if not zip_code:
            zip_code = (
                poi_html.xpath('.//p[@style="text-align: center;"]/text()')[-1]
                .split(", ")[-1]
                .split()[-1]
            )
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        phone = poi_html.xpath('//strong[contains(text(), "Phone:")]/following::text()')
        phone = phone[0].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = poi_html.xpath(".//iframe/@src")[0]
        geo = geo.split("!2d")[-1].split("!3m")[0].split("!3d")
        latitude = geo[-1]
        longitude = geo[0]
        hours_of_operation = "<MISSING>"

        if "Happy Valley" in street_address:
            street_address = street_address.split(", Happy Valley")[0]

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
