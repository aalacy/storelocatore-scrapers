import csv
import json
from lxml import etree
from urllib.parse import urljoin

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

    domain = "idealimage.com"
    start_url = "https://www.idealimage.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang="

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//store/item")
    for poi_html in all_locations:
        store_url = poi_html.xpath(".//exturl/text()")[0]
        store_url = urljoin("https://www.idealimage.com", store_url)

        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath('//script[contains(text(), "PostalAddress")]/text()')
        if poi:
            try:
                poi = json.loads(poi[0])
            except Exception:
                poi = json.loads(poi[0].replace("\n", "")[:-1])

            location_name = poi["name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["address"]["streetAddress"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["address"]["addressLocality"]
            city = city if city else "<MISSING>"
            state = poi["address"]["addressRegion"]
            state = state if state else "<MISSING>"
            zip_code = poi["address"].get("postalCode")
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = "<MISSING>"
            phone = poi["telephone"]
            phone = phone if phone else "<MISSING>"
            location_type = poi["@type"]
        else:
            location_name = poi_html.xpath(".//location/text()")
            location_name = location_name[0] if location_name else "<MISSING>"
            addr = parse_address_intl(poi_html.xpath(".//address/text()")[0])
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
            country_code = "<MISSING>"
            phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
            phone = phone[0] if phone else "<MISSING>"
            location_type = "<MISSING>"
        store_number = poi_html.xpath(".//storeid/text()")[0]
        latitude = poi_html.xpath(".//latitude/text()")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = poi_html.xpath(".//longitude/text()")
        longitude = longitude[0] if longitude else "<MISSING>"
        hoo = loc_dom.xpath('//table[@class="tbl-hours"]//text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        if not street_address:
            addr = parse_address_intl(
                " ".join(loc_dom.xpath('//div[@class="centeraddress"]//text()')[1:3])
            )
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        street_address = street_address if street_address else "<MISSING>"

        item = [
            domain,
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
