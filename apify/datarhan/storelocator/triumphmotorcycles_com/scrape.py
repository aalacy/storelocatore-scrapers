import re
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
    scraped_items = []

    DOMAIN = "triumphmotorcycles.com"

    start_url = "https://www.triumphmotorcycles.com/dealers/find-a-dealer?market=39&viewall=true#"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_poi_html = dom.xpath('//div[@class="dealerListItem"]')
    for poi_html in all_poi_html:
        store_url = poi_html.xpath('.//div[@class="websiteAddress"]//a/text()')
        store_url = store_url[0] if store_url else "<MISSING>"
        location_name = poi_html.xpath('.//span[@class="dealerName"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"

        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        address_raw = loc_dom.xpath(
            '//p[@class="dealer-location__address-text"]/span/text()'
        )
        if not address_raw:
            address_raw = loc_dom.xpath(
                '//div[@class="span4 dealerAddress"]/p[1]/text()'
            )
        address_raw = [
            elem.replace("<br/>", " ").strip()
            for elem in address_raw
            if elem.strip() and elem != ","
        ]
        addr = parse_address_intl(" ".join(address_raw))
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        street_address = street_address if street_address else "<MISSING>"
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//div[@class="dealerContact"]/span/text()')[1]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = loc_dom.xpath("//@data-map-lat")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = loc_dom.xpath("//@data-map-lon")
        longitude = longitude[0] if longitude else "<MISSING>"
        if latitude == "<MISSING>":
            geo = re.findall(r"LatLng\((.+?)\);", loc_response.text)[0].split(", ")
            latitude = geo[0]
            longitude = geo[1]
        hoo = loc_dom.xpath('//ul[@class="dealer-location__opening-times"]//text()')
        if not hoo:
            hoo = loc_dom.xpath('//div[@class="span4 dealerOpeningTimes"]/p/text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = ", ".join(hoo) if hoo else "<MISSING>"

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
