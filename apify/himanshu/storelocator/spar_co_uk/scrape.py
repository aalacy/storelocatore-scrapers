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

    start_url = "https://www.spar.co.uk/umbraco/api/storesearch/searchstores?maxResults=5&radius=10&startNodeId=1053&location=&filters=&lat={}&lng={}&filtermethod="
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = []
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN], max_radius_miles=10
    )
    for lat, lng in all_coords:
        response = session.get(start_url.format(lat, lng), headers=hdr)
        data = json.loads(response.text)
        if data.get("locations"):
            all_locations += data["locations"]

    for poi in all_locations:
        store_url = urljoin("https://www.spar.co.uk/", poi["url"])
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        loc = loc_dom.xpath('//script[contains(text(), "postalCode")]/text()')[-1]
        loc = json.loads(loc)

        location_name = poi.get("name")
        location_name = location_name if location_name else "<MISSING>"
        street_address = loc["address"].get("streetAddress")
        street_address = street_address if street_address else "<MISSING>"
        city = loc["address"].get("addressLocality")
        city = city if city else "<MISSING>"
        state = "<MISSING>"
        zip_code = loc["address"].get("postalCode")
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi.get("code")
        phone = poi.get("telephone")
        phone = phone if phone else "<MISSING>"
        location_type = poi.get("@type")
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi.get("lat")
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi.get("lng")
        longitude = longitude if longitude else "<MISSING>"
        hoo = []
        if loc.get("openingHoursSpecification"):
            for elem in loc["openingHoursSpecification"]:
                day = elem["dayOfWeek"][0]
                opens = elem["opens"]
                closes = elem["closes"]
                hoo.append(f"{day} {opens} {closes}")
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
        if store_number not in scraped_items:
            scraped_items.append(store_number)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
