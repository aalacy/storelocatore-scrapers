import csv
import json

from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


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
    scraped_items = []

    DOMAIN = "suntrust.com"

    all_codes = []
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], max_radius_miles=50
    )

    start_url = "https://www.mapquestapi.com/search/v2/radius?origin={}&radius=50&maxMatches=500&ambiguities=ignore&hostedData=mqap.32547_SunTrust_Branch_Loc&outFormat=json&key=Gmjtd|lu6zn1ua2d,70=o5-l0850"
    for code in all_codes:
        response = session.get(start_url.format(code))
        data = json.loads(response.text)
        if not data.get("searchResults"):
            continue

        for poi in data["searchResults"]:
            location_name = poi["name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["fields"]["address"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["fields"]["city"]
            city = city if city else "<MISSING>"
            state = poi["fields"]["state"]
            state = state if state else "<MISSING>"
            zip_code = poi["fields"]["postal"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["fields"]["country"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = poi["fields"]["RecordId"]
            store_number = store_number if store_number else "<MISSING>"
            phone = poi["fields"]["Phone_Published"]
            phone = phone if phone else "<MISSING>"
            summ = 0
            for key, value in poi["fields"].items():
                if "Is_" in key:
                    if not value:
                        continue
                    if type(value) != int:
                        continue
                    summ += int(value)
            location_type = ""
            if summ > 1:
                if poi["fields"]["Is_Branch"] == 1:
                    location_type = "branch"
            if summ == 1:
                if poi["fields"]["Is_ATM"] == 1:
                    location_type = "atm"
            if not location_type:
                location_type = "atm, branch"
            location_type = location_type if location_type else "<MISSING>"
            latitude = poi["fields"]["mqap_geography"]["latLng"]["lat"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["fields"]["mqap_geography"]["latLng"]["lng"]
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = poi["fields"]["Hours_Lobby_For_VRU"]
            hours_of_operation = (
                hours_of_operation if hours_of_operation else "<MISSING>"
            )

            store_url = "<MISSING>"
            if location_type != "<MISSING>":
                store_url = "https://www.suntrust.com/{}/{}/{}/{}/{}?location={}"
                location = "{} {} {}".format(
                    city, poi["fields"]["region_code"], zip_code
                )
                store_url = store_url.format(
                    location_type,
                    state,
                    city.replace(" ", "-"),
                    zip_code,
                    poi["fields"]["seo_name"],
                    location,
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

            if store_number not in scraped_items:
                scraped_items.append(store_number)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
