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
    scraped_items = []

    start_url = "https://wbliquors.com/stores/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//div[@data-store]")
    for poi_html in all_locations:
        liquor_sales = poi_html.xpath('.//span[contains(text(), "At Liquor Sales")]')
        if liquor_sales:
            continue
        store_url = poi_html.xpath(".//h4/a/@href")[0]
        if store_url in scraped_items:
            continue
        loc_response = session.get(store_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi_html.xpath(".//h4/a/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = location_name
        city = poi_html.xpath(".//address/text()")[0].split(", ")[0].strip()
        state = (
            poi_html.xpath(".//address/text()")[0].split(", ")[-1].split()[0].strip()
        )
        zip_code = (
            poi_html.xpath(".//address/text()")[0].split(", ")[-1].split()[-1].strip()
        )
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath(
            '//h4[contains(text(), "Contact")]/following-sibling::p[1]/text()'
        )
        phone = phone[0].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = loc_dom.xpath("//@data-lat")[0]
        longitude = loc_dom.xpath("//@data-lng")[0]
        hoo = poi_html.xpath('.//time[@itemprop="openingHours"]/text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
        if store_url not in scraped_items:
            scraped_items.append(store_url)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
