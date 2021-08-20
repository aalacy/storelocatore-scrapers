import re
import csv
import json
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

    start_url = "https://www.scores.ca/service/search/branch"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    response = session.get(start_url, headers=hdr)
    data = json.loads(response.text)

    for poi in data:
        store_url = urljoin(start_url, poi["slug"])
        location_name = poi["title"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["city"]
        city = city if city else "<MISSING>"
        state = poi["address"]["province"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["id"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        longitude = poi["lng"]
        hoo = ""
        if poi["open"]:
            hoo = []
            days = [
                "Lundi",
                "Mardi",
                "Mercredi",
                "Jeudi",
                "Vendredi",
                "Samedi",
                "Dimanche",
            ]
            for day in days:
                if poi["schedule"]["week"][day]["breakfast"]["range"]:
                    opens = poi["schedule"]["week"][day]["breakfast"]["range"][0][
                        "from"
                    ]
                    closes = poi["schedule"]["week"][day]["breakfast"]["range"][0]["to"]
                    hoo.append(f"{day} {opens} - {closes}")
                else:
                    hoo.append(f"{day} closed")
            hoo = " ".join(hoo)
        if not poi["open"]:
            hoo = "closed"
        hours_of_operation = hoo if hoo else "<MISSING>"

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
