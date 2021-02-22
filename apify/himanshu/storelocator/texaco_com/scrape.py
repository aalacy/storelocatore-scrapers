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
    start_url = "https://www.texaco.com/api/app/techron2go/ws_getChevronTexacoNearMe_r2.aspx?callback=jQuery22304128364136082625_1613584397139&lat=%s&lng=%s&oLat=%s&oLng=%s&brand=ChevronTexaco&radius=35"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
        "Content-Type": "application/json; charset=utf-8",
    }
    all_coordinates = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=10,
        max_search_results=None,
    )
    for lat, lng in all_coordinates:
        r = session.get(start_url % (lat, lng, lat, lng), headers=headers)
        lt = json.loads(
            r.text.split("jQuery22304128364136082625_1613584397139(")[1].split("})")[0]
            + "}"
        )
        for loc in lt["stations"]:
            store_url = (
                "https://www.texaco.com/find-gas-station/{}-{}-{}-{}-id{}".format(
                    loc["address"].replace(" ", "-").replace(".", ""),
                    loc["city"].replace(" ", "-"),
                    loc["state"],
                    loc["zip"],
                    loc["id"],
                )
            )
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
