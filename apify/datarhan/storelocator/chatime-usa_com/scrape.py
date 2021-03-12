import csv
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl


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

    DOMAIN = "chatime-usa.com"
    start_url = "https://chatime-usa.com/wp-admin/admin-ajax.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    formdata = {
        "action": "lsajax_search_results",
        "lat": "40.75368539999999",
        "lng": "-73.9991637",
        "distance": "50000",
        "distance_units": "km",
        "query_type": "postcode",
        "query_values[]": "10001",
        "query_values[]": "10001",
    }
    response = session.post(start_url, data=formdata, headers=headers)
    data = json.loads(response.text)

    for poi in data:
        poi_html = etree.HTML(poi["resultsItemHTML"])
        store_url = "<MISSING>"
        location_name = poi_html.xpath(".//h3/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath(".//address//text()")
        raw_address = [
            e.strip() for e in raw_address if e.strip() and "get " not in e.lower()
        ]
        raw_address = " ".join(raw_address)
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if not street_address:
            street_address = addr.street_address_2
        if not street_address:
            street_address = raw_address.split(",")[0]
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        zip_code = addr.postcode
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["i"]
        phone = poi_html.xpath('.//p[@class="lsform__result__details"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["lng"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = "<MISSING>"

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
