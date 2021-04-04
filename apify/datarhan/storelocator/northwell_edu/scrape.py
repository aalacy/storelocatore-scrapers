import re
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
    scraped_items = []

    DOMAIN = "northwell.edu"
    start_url = "https://www.northwell.edu/api/locations/108781?browse_all=true"

    all_poi = []

    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }
    url = "https://cdns.us1.gigya.com/sdk.config.getAPI?apiKey=3_FTxaSE9O0UuC4sKIHI0TdrJcPmvbKoNumROpQ5uDhkIDSk-4ooTzFaTG6nWd7T2p&pageURL=https%3A%2F%2Fwww.northwell.edu%2Fdoctors-and-care%2Flocations%3Fkeywords%3D%26zip%3DNew%2BYork%252C%2BNew%2BYork%2B10001%26type%3D"
    session.get(url, headers=hdr)
    session.get(
        "https://cdns.us1.gigya.com/sdk.config.getSSO?apiKey=3_e2Uo1FWkcXAk9b3hBYN3Mzuw1w91vVbVG0QNrLKKPZzNRdAh_cDdkilIKEhsHSLK&pageURL=https%3A%2F%2Fwww.northwell.edu",
        headers=hdr,
    )

    response = session.get(start_url, headers=hdr)
    data = json.loads(response.text)
    all_poi += data["results"]

    next_page = data["pagination"]["next"]
    while next_page:
        next_page = "https://www.northwell.edu" + next_page
        page_response = session.get(next_page, headers=hdr)
        page_data = json.loads(page_response.text)
        all_poi += page_data["results"]
        if type(page_data["pagination"]) != list:
            next_page = page_data["pagination"].get("next")
        else:
            next_page = None

    for poi in all_poi:
        store_url = poi.get("page_url")
        if store_url:
            if "https" not in store_url:
                store_url = "https:" + store_url
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi.get("title")
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi.get("street")
        if not street_address:
            continue
        if street_address:
            if poi.get("suite"):
                street_address += ", " + poi["suite"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi.get("city")
        city = city if city else "<MISSING>"
        state = poi.get("state")
        state = state if state else "<MISSING>"
        zip_code = poi.get("zip")
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi.get("phone")
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo_data = poi.get("map")
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if geo_data:
            geo_data = re.findall("markers=(.+),dod", poi["map"])[0].split(",")
            latitude = geo_data[-1]
            longitude = geo_data[0]

        store_response = session.get(store_url, headers=hdr)
        store_dom = etree.HTML(store_response.text)
        hours_of_operation = store_dom.xpath(
            '//div[@class="card__hours"]/table//text()'
        )
        hours_of_operation = " ".join(
            [elem.strip() for elem in hours_of_operation if elem.strip()][2:]
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
        check = "{} {}".format(location_name, street_address)
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
