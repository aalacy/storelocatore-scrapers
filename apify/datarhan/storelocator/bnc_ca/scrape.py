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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []
    scraped_items = []

    start_url = "https://localisateur.bnc.ca/?branch&atm"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    data = re.findall(r"setArrGeoCoord\((.+)\)", response.text)[0]
    all_locations = json.loads(data)

    for store_number, poi in all_locations.items():
        if poi["categoryIndex"] != "branch":
            continue
        store_url = poi["permalink"]
        location_name = poi["name"]
        street_address = poi["address"]
        city = poi["locality"]
        state = poi["region"]
        zip_code = poi["postcode"]
        country_code = poi["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["corporateId"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["categoryIndex"]
        latitude = poi["lat"]
        longitude = poi["lon"]
        hoo = etree.HTML(poi["storeHours"]).xpath("//text()")
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
        if hours_of_operation == "Non disponible":
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
        if store_number not in scraped_items:
            scraped_items.append(store_number)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
