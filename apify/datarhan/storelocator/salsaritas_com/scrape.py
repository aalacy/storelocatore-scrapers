import re
import csv
import json
from urllib.parse import urljoin
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

    DOMAIN = "salsaritas.com"
    start_url = "https://salsaritas.com/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    data = dom.xpath('//script[contains(text(), ".maps")]/text()')[0]
    data = re.findall(r"maps\((.+?)\).data", data.replace("\\n", "").replace("\\", ""))[
        0
    ]
    data = re.sub(r'list-map":"(.+?)","location-id', 'list-map":"","location-id', data)
    data = re.sub(
        r'infowindow_setting":"(.+?)","infowindow_bounce',
        'infowindow_setting":"","infowindow_bounce',
        data,
    )
    data = data.replace('140""', '140"')
    data = re.sub(
        r'infowindow_content":"(.+?)","content', 'infowindow_content":"","content', data
    )
    data = re.sub(
        r'%_wpgmp_map_id%":"(.+?)","%_wpgmp_metabox_marker_id',
        '%_wpgmp_map_id%":"","%_wpgmp_metabox_marker_id',
        data,
    )
    data = re.sub(
        r'wpgmp_metabox_marker_id%":"(.+?)","taxonomy',
        'wpgmp_metabox_marker_id%":"","taxonomy',
        data,
    )
    data = re.sub(
        r'ting_placeholder":"(.+?)"},"map_property',
        'ting_placeholder":""},"map_property',
        data,
    )
    data = json.loads(data.replace('[data-container="wpgmp-filters-container"]', ""))
    for poi in data["places"]:
        if poi.get("source"):
            if poi["source"] == "post":
                continue
        if poi.get("post_excerpt"):
            continue
        store_url = "<MISSING>"
        if poi["location"]["extra_fields"].get("landing"):
            store_url = urljoin(start_url, poi["location"]["extra_fields"]["landing"])
        location_name = poi["title"]
        street_address = poi["address"].split(", " + poi["location"]["city"])[0]
        city = poi["location"]["city"]
        city = city if city else "<MISSING>"
        if "Suit" not in street_address:
            street_address = street_address.split(", ")[0]
        street_address = street_address.replace(city, "")
        state = poi["location"]["state"]
        zip_code = poi["location"]["postal_code"]
        country_code = poi["location"]["country"]
        store_number = poi["id"]
        phone = poi["location"]["extra_fields"]["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["categories"][0]["name"]
        latitude = poi["location"]["lat"]
        longitude = poi["location"]["lng"]
        hours_of_operation = poi["location"]["extra_fields"]["opening-hours"].replace(
            "<br>", ""
        )
        hours_of_operation = hours_of_operation if hours_of_operation else "<MISSING>"

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
