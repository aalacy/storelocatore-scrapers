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

    start_url = (
        "https://econofitness.ca/fr/resultats?searchmode=searchall&searchtext=&filters="
    )
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "data_gym_map =")]/text()')[0]
    data = re.findall("data_gym_map = (.+)", data.replace("\n", ""))[0]
    data = json.loads(data)

    for poi in data:
        if not poi.get("urlinfo"):
            continue
        store_url = urljoin(start_url, poi["urlinfo"])
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        data = loc_dom.xpath('//script[contains(text(), "addressLocality")]/text()')[0]
        data = json.loads(data)

        location_name = data["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = data["address"]["streetAddress"]
        street_address = street_address if street_address else "<MISSING>"
        city = data["address"]["addressLocality"]
        city = city if city else "<MISSING>"
        state = (
            loc_dom.xpath('//div[@class="gym-address"]/text()')[0]
            .split(", ")[-1]
            .split()[0]
        )
        state = state if state else "<MISSING>"
        zip_code = poi["postalcode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = data["address"]["addressCountry"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        longitude = poi["long"]
        hoo = data["openingHours"]
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "closed"

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
