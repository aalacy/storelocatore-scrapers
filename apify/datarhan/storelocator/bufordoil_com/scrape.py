import re
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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "http://bufordoil.com/1/Our_Stores.html"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//p[a[contains(@href, "maps.google")]]')
    for poi_html in all_locations:
        store_url = start_url
        location_name = poi_html.xpath(".//preceding-sibling::p[1]/text()")
        location_name = (
            " ".join(location_name[0].split()) if location_name else "<MISSING>"
        )
        if "Omar" in location_name:
            location_name = "Omar’s Food Mart"
        if "Avenal" in location_name:
            location_name = "Avenal Food Mart"
        street_address = poi_html.xpath(".//a/text()")
        street_address = (
            " ".join(street_address[0].split()) if street_address else "<MISSING>"
        )
        city = poi_html.xpath(".//following-sibling::p[1]/text()")[0].split(", ")[0]
        state = (
            poi_html.xpath(".//following-sibling::p[1]/text()")[0]
            .split(", ")[-1]
            .split()[0]
        )
        zip_code = (
            poi_html.xpath(".//following-sibling::p[1]/text()")[0]
            .split(", ")[-1]
            .split()[-1]
        )
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath(".//following-sibling::p[2]/text()")
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = (
            poi_html.xpath(".//a/@href")[0].split("&sll=")[-1].split("&")[0].split(",")
        )
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if len(geo) == 2:
            latitude = geo[0]
            longitude = geo[1]
        hours_of_operation = "<MISSING>"

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
