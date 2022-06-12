import csv
import json
from lxml import etree

from sgrequests import SgRequests


base_url = "https://www.additionelle.com"


def validate(item):
    if item is None:
        item = ""
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = " ".join(item)
    return item.strip()


def get_value(item):
    if item is None:
        item = "<MISSING>"
    item = validate(item)
    if item == "":
        item = "<MISSING>"
    return item


def eliminate_space(items):
    rets = []
    for item in items:
        item = validate(item)
        if item != "":
            rets.append(item)
    return rets


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    items = []

    DOMAIN = "additionelle.com"
    start_url = "https://www.additionelle.com/mobify/proxy/base/s/Additionelle_CA/dw/shop/v18_8/stores?country_code=CA&postal_code=K1P1B1&max_distance=20000&count=200&locale=default"

    session = SgRequests()
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
        "x-dw-client-id": "a5880415-96c2-4fe1-8d1e-a70a343dfe69",
    }
    request = session.get(start_url, headers=headers)
    data = json.loads(request.text)
    if "data" in data:
        all_locations = data["data"]
        for poi in all_locations:
            location_name = poi["name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["address1"]
            if poi.get("address2"):
                street_address += " " + poi["address2"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["city"]
            city = city if city else "<MISSING>"
            state = poi["state_code"]
            zip_code = poi["postal_code"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["country_code"]
            store_number = poi["id"]
            phone = poi["phone"]
            location_type = poi["_type"]
            latitude = poi["latitude"]
            longitude = poi["longitude"]
            hoo = []
            if poi.get("store_hours"):
                hoo = etree.HTML(poi["store_hours"]).xpath("//text()")
                hoo = [e.strip() for e in hoo if e]
            hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
            store_url = "https://locations.penningtons.com/{}-{}-{}"
            store_url = store_url.format(
                state.lower(), city.replace(" ", "-").lower(), store_number
            )

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
