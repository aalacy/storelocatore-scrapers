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

    DOMAIN = "binsons.com"
    start_url = "https://www.binsons.com/modules/locations/library/gmap.php"

    formdata = {"types": "", "services": "", "search": "", "states": ""}
    response = session.post(start_url, data=formdata)
    data = json.loads(response.text)

    for poi in data:
        store_url = "https://www.binsons.com/locations/{}"
        store_url = store_url.format(
            poi["Name"]
            .replace(" ", "-")
            .replace(",", "")
            .replace(".", "")
            .replace("(", "")
            .replace(")", "")
            .replace(".", "")
            .replace("&", "and")
        )
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi["Name"]
        location_name = location_name if location_name else "<MISSING>"
        raw_adr = loc_dom.xpath('//p[@class="location-address my-1"]/text()')
        street_address = raw_adr[0]
        city = raw_adr[-1].split(", ")[0]
        state = raw_adr[-1].split(", ")[-1].split()[0]
        zip_code = raw_adr[-1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = poi["id"]
        phone = loc_dom.xpath('//p[@class="location-phone-main my-1"]/text()')
        phone = phone[-1].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["Lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["Lng"]
        longitude = longitude if longitude else "<MISSING>"
        hoo = loc_dom.xpath('//div[@class="location-hours-list"]//text()')
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
