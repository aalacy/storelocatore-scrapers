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
    session = SgRequests()

    items = []

    DOMAIN = "aaa.com"
    start_url = "https://calstate.aaa.com/agent-office-locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = []
    all_urls = dom.xpath('//a[@class="Directory-listLink"]/@href')
    for url in all_urls:
        if len(url.split("/")) == 3:
            all_locations.append(url)
            continue
        response = session.get(urljoin(start_url, url))
        dom = etree.HTML(response.text)
        all_locations += [
            urljoin(response.url, url)
            for url in dom.xpath('//a[@class="Teaser-titleLink"]/@href')
        ]
        sub_urls = dom.xpath('//a[@class="Directory-listLink"]/@href')
        for url in sub_urls:
            if len(url.split("/")) == 3:
                all_locations.append(url)
                continue
            response = session.get(urljoin(start_url, url))
            dom = etree.HTML(response.text)
            all_locations += [
                urljoin(response.url, url)
                for url in dom.xpath('//a[@class="Teaser-titleLink"]/@href')
            ]

    for url in list(set(all_locations)):
        if "http" not in url:
            store_url = "https://calstate.aaa.com/agent-office-locations/" + url
        else:
            store_url = url
        store_url = store_url.replace("/az/az/", "/az/")
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath('//script[@id="js-map-config-dir-map"]/text()')[0]
        poi = json.loads(poi)

        location_name = poi["entities"][0]["profile"]["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["entities"][0]["profile"]["address"]["line1"]
        if poi["entities"][0]["profile"]["address"]["line2"]:
            street_address += ", " + poi["entities"][0]["profile"]["address"]["line2"]
        city = poi["entities"][0]["profile"]["address"]["city"]
        state = poi["entities"][0]["profile"]["address"]["region"]
        zip_code = poi["entities"][0]["profile"]["address"]["postalCode"]
        country_code = poi["entities"][0]["profile"]["address"]["countryCode"]
        store_number = "<MISSING>"
        phone = poi["entities"][0]["profile"]["mainPhone"]["number"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["entities"][0]["profile"].get("c_branchType")
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["entities"][0]["profile"]["yextDisplayCoordinate"]["lat"]
        longitude = poi["entities"][0]["profile"]["yextDisplayCoordinate"]["long"]
        hours_of_operation = loc_dom.xpath('//table[@class="c-hours-details"]//text()')[
            2:
        ]
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

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
