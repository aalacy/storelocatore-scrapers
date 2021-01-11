import csv
from sgrequests import SgRequests
import json
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("gamestop_com")
session = SgRequests()

base_url = "https://www.gamestop.com/"


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    headers = {
        "accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "referer": "https://www.gamestop.com/stores/?showMap=true&horizontalView=true&isForm=true",
    }
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        max_radius_miles=50,
        max_search_results=2000,
    )
    for lat, lng in search:
        url = (
            "https://www.gamestop.com/on/demandware.store/Sites-gamestop-us-Site/default/Stores-FindStores?radius=400&lat="
            + str(lat)
            + "&long="
            + str(lng)
            + ""
        )
        data = session.get(url, headers=headers, data={}).text
        json_data = json.loads(data)
        if "stores" in json_data:
            for store in json_data["stores"]:
                try:
                    location_name = store["name"]
                except:
                    location_name = "<MISSING>"

                try:
                    street_address = store["address1"] + ", " + store["address2"]
                except:
                    street_address = "<MISSING>"

                try:
                    city = store["city"]
                except:
                    city = "<MISSING>"

                try:
                    state = store["stateCode"]
                except:
                    state = "<MISSING>"

                try:
                    zip = store["postalCode"]
                except:
                    zip = "<MISSING>"

                try:
                    country_code = store["countryCode"]
                except:
                    country_code = "<MISSING>"

                try:
                    store_number = store["ID"]
                except:
                    store_number = "<MISSING>"

                try:
                    phone = store["phone"]
                except:
                    phone = "<MISSING>"

                try:
                    location_type = "<MISSING>"
                except:
                    location_type = "<MISSING>"

                try:
                    latitude = store["latitude"]
                except:
                    latitude = "<MISSING>"

                try:
                    longitude = store["longitude"]
                except:
                    longitude = "<MISSING>"

                try:
                    hours_of_operation = store["storeHours"]
                except:
                    hours_of_operation = "<MISSING>"

                try:
                    page_url = (
                        "https://www.gamestop.com/store/us/"
                        + str(store["stateCode"])
                        + "/"
                        + str(store["city"])
                        + "/"
                        + str(store["ID"])
                    )
                except:
                    page_url = "<MISSING>"
                store = []
                store.append("http://www.gamestop.com")
                store.append(location_name if location_name else "<MISSING>")
                store.append(
                    street_address.replace(" None", "")
                    if street_address
                    else "<MISSING>"
                )
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zip if zip else "<MISSING>")
                store.append(country_code if country_code else "<MISSING>")
                store.append(store_number if store_number else "<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append(location_type if location_type else "<MISSING>")
                store.append(latitude if latitude else "<MISSING>")
                store.append(longitude if longitude else "<MISSING>")
                store.append(hours_of_operation if hours_of_operation else "<MISSING>")
                store.append(page_url)
                if store[2] in addresses:
                    continue
                addresses.append(store[2])
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
