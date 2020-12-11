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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []

    DOMAIN = "lukoilamericas.com"
    start_url = "https://lukoilamericas.com/api/cartography/GetCountryDependentSearchObjectData?form=gasStation&country=US"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }
    allpoints_response = session.get(start_url, verify=False)
    data = json.loads(allpoints_response.text)
    for elem in data["GasStations"]:
        gs_url = "https://lukoilamericas.com/api/cartography/GetObjects?ids=gasStation{}&lng=ENelem".format(
            elem["GasStationId"]
        )

        gs_response = session.get(gs_url, headers=headers)
        poi = json.loads(gs_response.text)[0]

        if not poi["GasStation"]["Company"]["Name"] == "Lukoil Americas Corporation":
            continue

        store_url = "https://lukoilamericas.com/en/ForMotorists/PetrolStations/PetrolStation?type=gasStation&id={}".format(
            elem["GasStationId"]
        )
        location_name = "Station №" + str(poi["GasStation"]["Name"])
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["GasStation"]["Street"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["GasStation"]["City"]
        city = city if city else "<MISSING>"
        state = poi["GasStation"]["Address"].split(",")[-2]
        if len(state.strip()) > 2:
            state = poi["GasStation"]["Address"].split(",")[-1].split()[0]
        state = state.strip() if state else "<MISSING>"
        zip_code = poi["GasStation"]["PostCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["GasStation"]["StationNumber"]
        phone = "<MISSING>"
        location_type = "gasStation"
        latitude = poi["GasStation"]["Latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["GasStation"]["Longitude"]
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
