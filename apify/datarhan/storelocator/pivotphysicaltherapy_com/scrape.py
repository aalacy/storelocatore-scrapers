import csv
import json
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

    DOMAIN = "pivotphysicaltherapy.com"
    start_url = "https://www.pivotphysicaltherapy.com/locations/"
    post_url = "https://www.pivotphysicaltherapy.com/wp-admin/admin-ajax.php"

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }

    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)
    states = dom.xpath('//a[@class="map-state"]/@data-state')
    for state in states:
        formadata = {
            "action": "markersearch",
            "method": "sate",
            "state": state,
            "zip": "",
            "lat": "",
            "lng": "",
            "radius": "",
            "service": "",
            "tmpl": "locations",
        }

        headers_post = {
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }

        response = session.post(post_url, data=formadata, headers=headers_post)
        data = json.loads(response.text)

        for poi in data["markers"]:
            store_url_html = etree.HTML(poi["list_format"])
            store_url = store_url_html.xpath(".//a/@href")[0]
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)
            location_name = poi["name"]
            location_name = location_name if location_name else "<MISSING>"
            street_data = loc_dom.xpath("//address//text()")
            street_data = [elem.strip() for elem in street_data if elem.strip()]
            addr = parse_address_intl(" ".join(street_data))
            street_address = addr.street_address_1.strip()
            if addr.street_address_2:
                street_address += " " + addr.street_address_2.strip()
            if street_address[0] == ",":
                street_address = street_address[1:].strip()
            city = addr.city
            city = city if city else "<MISSING>"
            zip_code = addr.postcode
            zip_code = zip_code if zip_code else "<MISSING>"
            state = addr.state
            state = state if state else "<MISSING>"
            country_code = "<MISSING>"
            store_number = poi["id"]
            store_number = store_number if store_number else "<MISSING>"
            phone = loc_dom.xpath('//div[@class="location-phone"]/text()')
            phone = phone[1].strip().replace("Phone ", "") if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = poi["lat"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["lng"]
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = loc_dom.xpath(
                '//h2[contains(text(), "HOURS")]/following-sibling::div/table//td/text()'
            )
            hours_of_operation = (
                ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
            )

            if len(street_data) == 4:
                street_address = ", ".join(street_data[:-1])

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
