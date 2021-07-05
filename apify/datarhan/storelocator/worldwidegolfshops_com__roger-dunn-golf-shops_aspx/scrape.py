import re
import csv
import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgselenium import SgFirefox


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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://www.worldwidegolfshops.com/roger-dunn-golf-shops"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[@class="store-name-link"]/@href')
    for store_url in all_locations:
        store_url = urljoin(start_url, store_url)

        if "worldwidegolfshops" in store_url:
            with SgFirefox() as driver:
                driver.get(store_url)
                loc_dom = etree.HTML(driver.page_source)
            poi = loc_dom.xpath('//script[@type="application/ld+json"]/text()')[0]
            poi = json.loads(poi)

            location_name = loc_dom.xpath("//h1/text()")[0]
            street_address = poi["address"]["streetAddress"]
            city = poi["address"]["addressLocality"]
            state = poi["address"]["addressRegion"]
            zip_code = poi["address"]["postalCode"]
            country_code = "<MISSING>"
            store_number = poi["@id"]
            phone = poi["telephone"]
            location_type = poi["@type"][0]
            latitude = poi["geo"]["latitude"]
            longitude = poi["geo"]["longitude"]
            hoo = loc_dom.xpath(
                '//div[contains(text(), "STORE HOURS")]/following-sibling::div//text()'
            )
        else:
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)
            poi = loc_dom.xpath("//@data-block-json")[0]
            poi = json.loads(poi)

            location_name = loc_dom.xpath("//h1/text()")[0]
            street_address = poi["location"]["addressLine1"]
            city = poi["location"]["addressLine2"].split(", ")[0]
            state = poi["location"]["addressLine2"].split(", ")[1].split()[0]
            zip_code = poi["location"]["addressLine2"].split(", ")[-1].split()[-1]
            country_code = poi["location"]["addressCountry"]
            store_number = "<MISSING>"
            phone = loc_dom.xpath(
                '//p[strong[contains(text(), "Phone")]]/following-sibling::p/text()'
            )[0]
            location_type = "<MISSING>"
            latitude = poi["location"]["mapLat"]
            longitude = poi["location"]["mapLng"]
            hoo = loc_dom.xpath(
                '//p[strong[contains(text(), "HOURS")]]/following-sibling::p/text()'
            )[:-1]
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
