import csv

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
    session = SgRequests()

    zips = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=200,
        max_search_results=None,
    )
    return_main_object = []
    addresses = []
    for zip_code in zips:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
        }
        r = session.get(
            "https://www.lexus.com/rest/dealersByZipAndPma/" + str(zip_code),
            headers=headers,
        )
        data = r.json()["data"]
        for store_data in data:
            store = []
            store.append(
                "https://www.lexus.com/dealers/{}-{}".format(
                    store_data["id"], store_data["dealerName"].replace(" ", "-").lower()
                )
            )
            store.append(store_data["dealerName"])
            street_adr = store_data["dealerAddress"]["address1"]
            if store_data["dealerAddress"]["address2"]:
                street_adr += " " + store_data["dealerAddress"]["address2"]
            store.append(street_adr)
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(store_data["dealerAddress"]["city"])
            store.append(store_data["dealerAddress"]["state"])
            store.append(store_data["dealerAddress"]["zipCode"])
            store.append("US")
            store.append(store_data["id"])
            store.append(store_data["dealerPhone"])
            store.append("lexus")
            store.append(store_data["dealerLatitude"])
            store.append(store_data["dealerLongitude"])
            if store_data["hoursOfOperation"] != {} and store_data[
                "hoursOfOperation"
            ].get("Sales"):
                hours = ""
                store_hours = store_data["hoursOfOperation"]["Sales"]
                for key in store_hours:
                    hours = hours + " " + key + " " + store_hours[key]
                store.append(hours if hours != "" else "<MISSING>")
            else:
                store.append("<MISSING>")
            return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
