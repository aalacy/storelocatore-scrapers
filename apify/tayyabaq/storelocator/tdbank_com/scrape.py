import re
import csv
import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


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

    start_url = "https://locations.td.com/index.html?q={},{}&qp=&locType=stores&l=en"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "accept": "application/json",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    }

    all_locations = []
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], max_radius_miles=50
    )
    for lat, lng in all_coords:
        response = session.get(start_url.format(lat, lng), headers=hdr)
        data = json.loads(response.text)
        all_locations += data["response"]["entities"]

    for poi in all_locations:
        store_url = urljoin(start_url, poi["url"])
        location_name = poi["profile"]["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["profile"]["address"]["line1"]
        if poi["profile"]["address"]["line2"]:
            street_address += " " + poi["profile"]["address"]["line2"]
        if poi["profile"]["address"]["line3"]:
            street_address += " " + poi["profile"]["address"]["line3"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["profile"]["address"]["city"]
        city = city if city else "<MISSING>"
        state = poi["profile"]["address"]["region"]
        state = state if state else "<MISSING>"
        zip_code = poi["profile"]["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["profile"]["address"]["countryCode"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["profile"].get("c_basicStoreID")
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["profile"]["mainPhone"]["display"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if poi["profile"].get("geocodedCoordinate"):
            latitude = poi["profile"]["geocodedCoordinate"]["lat"]
            longitude = poi["profile"]["geocodedCoordinate"]["long"]

        check = f"{location_name} {street_address}"
        if check in scraped_items:
            continue
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        hoo = loc_dom.xpath(
            '//div[@class="c-hours-details-wrapper js-hours-table"]//text()'
        )[1:]
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo).split("{")[0].strip() if hoo else "<MISSING>"

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

        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
