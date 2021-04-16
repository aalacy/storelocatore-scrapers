import re
import csv
import json

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

    DOMAIN = "auntieannes.co.uk"
    start_url = "https://pretzelhq.auntieannes.co.uk/services/store/allstores?callback=jQuery110205844335164275849_1613591033158&_=1613591033159"

    response = session.get(start_url)
    data = re.findall(r"storeData\((.+)\);", response.text)[0]
    data = json.loads(data)

    for poi in data:
        store_url = poi["ShoppingCentreUrl"]
        if store_url and ".ie" in store_url:
            continue
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["Name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["Address"]["Line1"]
        if poi["Address"]["Line2"]:
            street_address += " " + poi["Address"]["Line2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["Address"]["Town"]
        city = city if city else "<MISSING>"
        state = poi["Address"]["County"]
        state = state if state else "<MISSING>"
        zip_code = poi["Address"]["Postcode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["Id"]
        phone = "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["Address"]["Latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["Address"]["Longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hoo = []
        for elem in poi["StoreTradings"]:
            day = elem["DayOfWeekDescription"]
            opens = elem["OpeningTime"]
            closes = elem["ClosingTime"]
            hoo.append(f"{day} {opens} - {closes}")
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
