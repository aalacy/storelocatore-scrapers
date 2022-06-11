import csv
import json

from sgrequests import SgRequests

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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://www.bmw.ca/c2b-localsearch/services/api/v4/clients/BMWSTAGE2_DLO/digitalstage2_CA/pois?brand=BMW_BMWM&cached=off&callback=angular.callbacks._0&category=BM&country=CA&language=en&lat=0&lng=0&maxResults=700&showAll=true&unit=km"
    return_main_object = []
    api_request = session.get(base_url, headers=headers)
    location_data = json.loads(
        api_request.text.split("angular.callbacks._0(")[1].split("})")[0] + "}"
    )["data"]["pois"]
    for store_data in location_data:
        store = []
        store.append("https://www.bmw.ca")
        store.append(store_data["name"])
        store.append(store_data["street"])
        city = store_data["city"]
        store.append(city)
        if "Sainte-Agathe" in city:
            state = "QC"
        else:
            state = store_data["state"]
        store.append(state)
        store.append(store_data["postalCode"])
        store.append(store_data["countryCode"])
        store.append(store_data["key"])
        store.append(store_data["attributes"]["phone"])
        store.append("<MISSING>")
        store.append(store_data["lat"])
        store.append(store_data["lng"])
        store.append("<MISSING>")
        store.append(store_data["attributes"]["homepage"])
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
