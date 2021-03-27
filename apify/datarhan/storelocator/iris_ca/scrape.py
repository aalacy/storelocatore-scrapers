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

    start_url = "https://iris.ca/en/find-a-store/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "__SLS_REDUX_STATE__")]/text()')[0]
    data = re.findall("SLS_REDUX_STATE__ =(.+);", data)[0]
    data = json.loads(data)

    all_ids = []
    for elem in data["dataLocations"]["collection"]["features"]:
        all_ids.append(str(elem["properties"]["id"]))

    params = {
        "locale": "en_CA",
        "ids": ",".join(all_ids),
        "clientId": "587e629420d63ace17da9a05",
        "cname": "iris-sweetiq-sls-production.sweetiq.com",
    }
    url = "https://sls-api-service.sweetiq-sls-production-west.sweetiq.com/IVltr82YbCa5QgACToun0x8jstGlTO/locations-details"
    response = session.get(url, params=params)
    data = json.loads(response.text)

    for poi in data["features"]:
        store_url = urljoin(start_url, poi["properties"]["slug"])
        location_name = poi["properties"]["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["properties"]["addressLine1"]
        if poi["properties"]["addressLine2"]:
            street_address += " " + poi["properties"]["addressLine2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["properties"]["city"]
        city = city if city else "<MISSING>"
        state = poi["properties"]["province"]
        state = state if state else "<MISSING>"
        zip_code = poi["properties"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["properties"]["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["properties"]["branch"]
        phone = poi["properties"]["phoneNumber"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["geometry"]["coordinates"][1]
        longitude = poi["geometry"]["coordinates"][0]
        hoo = []
        for day, hours in poi["properties"]["hoursOfOperation"].items():
            if hours:
                opens = hours[0][0]
                closes = hours[0][1]
                hoo.append(f"{day} {opens} - {closes}")
            else:
                hoo.append(f"{day} {opens} - {closes}")
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
