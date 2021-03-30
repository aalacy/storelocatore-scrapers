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

    DOMAIN = "maseratiusa.com"

    start_url = "https://www.geocms.it/Server/servlet/S3JXServletCall?parameters=method_name%3DGetObject%26callback%3Dscube.geocms.GeoResponse.execute%26id%3D1%26clear%3Dtrue%26query%3D(%255Bsales%255D%253D%255Btrue%255D%2520OR%2520%255Bassistance%255D%253D%255Btrue%255D)%2520AND%2520%255BcountryIsoCode2%255D%253D%255BUS%2520OR%2520us%255D%26licenza%3Dgeo-maseratispa%26progetto%3DDealerLocator%26lang%3DALL&encoding=UTF-8"
    response = session.get(start_url)
    data = re.findall(r'execute\("(.+)","",1\)', response.text)[0]

    data = json.loads(data.replace("\\", ""))
    for poi in data["L"][0]["O"]:
        store_url = poi["U"].get("url")
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["U"].get("dealername")
        if not location_name:
            continue
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["U"]["address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["U"]["city"]
        city = city if city else "<MISSING>"
        state = poi["U"].get("province")
        state = state if state else "<MISSING>"
        zip_code = poi["U"]["postcode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["U"]["countryIsoCode2"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["U"]["dealercode"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["U"].get("phone")
        phone = phone if phone else "<MISSING>"
        if len(phone.strip()) < 2:
            phone = "<MISSING>"
        location_type = ""
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["G"][0]["P"][0]["y"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["G"][0]["P"][0]["x"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        days = {
            "1": "Monday",
            "2": "Tuesday",
            "3": "Wednesday",
            "4": "Thursday",
            "5": "Friday",
            "6": "Saturday",
            "7": "Sunday",
        }
        for elem in poi["U"]["G"]["opening_hours"]:
            day = days[elem["giorno"]]
            if elem.get("pmTo"):
                hours = "{} - {}".format(elem["amFrom"], elem["pmTo"])
            else:
                hours = "{} - {}".format(elem["amFrom"], elem["amTo"])
            hours_of_operation.append("{} {}".format(day, hours))
        hours_of_operation = (
            ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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
