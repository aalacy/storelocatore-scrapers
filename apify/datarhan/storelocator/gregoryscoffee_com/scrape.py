import re
import csv
import json
from lxml import etree
from urllib.parse import urljoin

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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://www.gregoryscoffee.com/locations"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath("//@locations_map")[0]
    data = json.loads(data)

    for key in data.keys():
        for poi in data[key]:
            store_url = urljoin(start_url, poi["slug"])
            location_name = poi["name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["address_line"].split(" - ")[0]
            city = poi["city"]
            city = city if city else "<MISSING>"
            raw_data = poi["secondary_address"].split(", ")
            state = raw_data[1]
            zip_code = raw_data[2]
            country_code = "<MISSING>"
            store_number = poi["id"]
            phone = poi["phone"]
            phone = phone if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = poi["lat"]
            longitude = poi["lng"]
            hoo = []
            if poi["business_hours"]:
                hoo = etree.HTML(poi["business_hours"])
                if hoo:
                    hoo = hoo.xpath("//text()")
                    hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = " ".join(hoo).replace("\n", "") if hoo else "<MISSING>"

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
