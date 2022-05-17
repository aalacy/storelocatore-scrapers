import csv
import json
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import sglog
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
    logger = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    session = SgRequests()

    items = []

    DOMAIN = "atd-us.com"
    start_url = "https://www.atd-us.com/atdcewebservices/v2/atdus/warehouse/search?latlong={},{}&distance=1000&lang=en&curr=USD"

    all_coordinates = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_results=100,
    )

    headers = {}
    headers["Content-Type"] = "application/json"
    headers["Content-Length"] = "0"

    def get_auth():
        auth_url = "https://www.atd-us.com/authorizationserver/oauth/token?client_id=atd-ce&client_secret=secret&grant_type=client_credentials"
        auth = session.post(auth_url, headers=headers).json()
        return str(auth["token_type"] + " " + auth["access_token"])

    headers["Authorization"] = get_auth()
    headers["Host"] = "www.atd-us.com"
    headers["X-Anonymous-Consents"] = "%5B%5D"
    headers["Accept"] = "application/json, text/plain, */*"
    headers[
        "User-Agent"
    ] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"

    identities = set()
    maxZ = all_coordinates.items_remaining()
    total = 0

    for lat, lng in all_coordinates:
        response = session.get(start_url.format(lat, lng), headers=headers)
        data = json.loads(response.text)
        found = 0
        coords = []
        try:
            data["warehouseList"] = data["warehouseList"]
        except Exception:
            headers["Authorization"] = get_auth()
            response = session.get(start_url.format(lat, lng), headers=headers)
            data = json.loads(response.text)

        for poi in data["warehouseList"]:
            store_url = "<MISSING>"
            location_name = poi["addressData"]["line1"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["addressData"]["line2"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["addressData"]["town"]
            city = city if city else "<MISSING>"
            state = poi["addressData"]["region"]["isocodeShort"]
            state = state if state else "<MISSING>"
            zip_code = poi["addressData"]["postalCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = "<MISSING>"
            store_number = poi["dcCode"]
            store_number = store_number if store_number else "<MISSING>"
            phone = poi["addressData"].get("phone")
            phone = phone if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = poi["addressData"]["latlong"].split(",")[0]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["addressData"]["latlong"].split(",")[-1]
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = "<MISSING>"
            latlong = (latitude, longitude)
            coords.append(latlong)

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

            if store_number not in identities:
                identities.add(store_number)
                items.append(item)
                found += 1
        progress = str(round(100 - (all_coordinates.items_remaining() / maxZ * 100), 2))
        total += found
        logger.info(
            f"{round(lat,4)}, {round(lng,4)} | found: {found} | total: {total} | progress: {progress}"
        )
        [all_coordinates.found_location_at(latitude=_y,longitude=_x) for _y, _x in coords]

    logger.info(f"Finished grabbing data!!")  # noqa
    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
