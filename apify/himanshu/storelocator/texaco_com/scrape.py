import csv
import json

from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


session = SgRequests()


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
    items = []
    scraped_items = []

    DOMAIN = "texaco.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
        "Content-Type": "application/json; charset=utf-8",
    }

    all_coordinates = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=50,
        max_search_results=None,
    )
    for lat, lng in all_coordinates:
        r = session.get(
            f"https://www.texaco.com/api/app/techron2go/ws_getChevronTexacoNearMe_r2.aspx?callback=jQuery22306785250418595727_1564653077932&lat={lat}&lng={lng}&oLat={lat}&oLng={lng}&brand=ChevronTexaco&radius=100&_=1564653077933",
            headers=headers,
        )
        lt = json.loads(
            r.text.split("jQuery22306785250418595727_1564653077932(")[1].split("})")[0]
            + "}"
        )
        for loc in lt["stations"]:
            store_url = "<MISSING>"
            location_name = loc["name"]
            city = loc["city"]
            street_address = loc["address"]
            state = loc["state"]
            zip_code = loc["zip"]
            country_code = "US"
            location_type = "<MISSING>"
            store_number = loc["id"]
            phone = loc["phone"]
            phone = phone if phone else "<MISSING>"
            latitude = loc["lat"]
            longitude = loc["lng"]
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
            if store_number not in scraped_items:
                scraped_items.append(store_number)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
