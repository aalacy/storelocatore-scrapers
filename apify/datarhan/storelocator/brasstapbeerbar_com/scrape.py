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

    DOMAIN = "brasstapbeerbar.com"
    start_url = "https://www.brasstapbeerbar.com/pinsNearestBrassTap.ashx?lat1=27.950&lon1=-82.45&range=10000&food=%25&lunch=%25&brunch=%25&music=%25"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data:
        store_url = ""
        if poi["urltag"]:
            store_url = "https://www.brasstapbeerbar.com/" + poi["urltag"]
        if not store_url:
            store_url = poi["onlineordering"]
        store_url = store_url if store_url else "<MISSING>"
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi["title"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]
        street_address = street_address.strip() if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["zip"]
        zip_code = zip_code.strip() if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["storeID"]
        phone = loc_dom.xpath('//div[@itemprop="telephone"]/a/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["lng"]
        longitude = longitude if longitude else "<MISSING>"
        hoo = loc_dom.xpath(
            '//div[@class="frame hours"]//div[@class="box list"]//text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
        if "This location isn" in hours_of_operation:
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
