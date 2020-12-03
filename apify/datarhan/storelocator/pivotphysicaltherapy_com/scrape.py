import csv
import json
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
        }

        headers_post = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }

        response = session.post(post_url, data=formadata, headers=headers_post)
        data = json.loads(response.text)

        for poi in data["markers"]:
            store_url_html = etree.HTML(poi["list_format"])
            store_url = store_url_html.xpath(".//a/@href")[0]
            store_response = session.get(store_url, headers=headers)
            store_dom = etree.HTML(store_response.text)
            location_name = poi["name"]
            location_name = location_name if location_name else "<MISSING>"
            street_data = store_dom.xpath("//address/text()")
            street_data = [elem.strip() for elem in street_data]
            street_address = street_data[0]
            if "Ste" in street_data[1]:
                street_address += ", " + street_data[1]
            city = street_data[-1].split(",")[0].strip()
            zip_code = street_data[-1].split(",")[-1].split()[-1].strip()
            state = street_data[-1].split(",")[-1].split()[0].strip()
            country_code = "<MISSING>"
            store_number = poi["id"]
            store_number = store_number if store_number else "<MISSING>"
            phone = store_dom.xpath('//div[@class="location-phone"]/text()')
            phone = phone[0].strip().replace("Phone ", "") if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = poi["lat"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["lng"]
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = store_dom.xpath(
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
