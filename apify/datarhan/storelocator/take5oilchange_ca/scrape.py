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

    start_url = "https://api.prooil.ca/api/stores/states/"
    domain = "take5oilchange.ca"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_locations = []
    response = session.get(start_url, headers=hdr)
    data = json.loads(response.text)
    for state in data["message"]:
        for city in state["cities"]:
            all_locations += city["stores"]

    for poi in all_locations:
        store_url = poi["storeURL"]
        if store_url:
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)
        else:
            store_url = store_url if store_url else "<MISSING>"

        location_name = "TAKE 5 OIL CHANGE #{}".format(str(poi["storeId"]))
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["streetAddress1"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["locationCity"]
        city = city if city else "<MISSING>"
        state = poi["locationState"]
        state = state if state else "<MISSING>"
        zip_code = poi["locationPostalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["locationCountry"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["storeId"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        longitude = poi["lng"]
        hoo = []
        if store_url != "<MISSING>":
            hoo = loc_dom.xpath(
                '//div[@class="store-hours font-opensans font-16"]/p/text()'
            )
            hoo = [" ".join([s for s in e.split()]) for e in hoo if e.strip()]
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
