import csv
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("navyfederal_org")

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_radius_miles=100,
    max_search_results=None,
)

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    for lat, lng in search:
        result_coords = []
        x = lat
        y = lng
        url = (
            "https://mweb.navyfederal.org/unauth/Locator/services/coordLocation/v2/lat/"
            + str(lat)
            + "/lon/"
            + str(lng)
            + "/dist/50/loc/50/"
        )
        logger.info("%s - %s..." % (str(x), str(y)))
        r = session.get(url, headers=headers)
        data = r.json()["coordLocation"]["data"]["locations"]
        for store_data in data:
            if store_data["country"] != "USA":
                continue
            lat = store_data["lat"]
            lng = store_data["lon"]
            result_coords.append((lat, lng))
            store = []
            store.append("navyfederal.org")
            store.append("<MISSING>")
            store.append(store_data["name"])
            store.append(store_data["address"])
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(store_data["city"] if "city" in store_data else "<MISSING>")
            store.append(store_data["state"] if "state" in store_data else "<MISSING>")
            store.append(
                store_data["zipcode"] if "zipcode" in store_data else "<MISSING>"
            )
            if not store[-1].split("-")[0].isdigit():
                store[-1] = "<MISSING>"
            store.append("US")
            store.append("<MISSING>")
            store.append(
                store_data["phone"]
                if "phone" in store_data
                and store_data["phone"] != ""
                and store_data["phone"] is not None
                else "<MISSING>"
            )
            store.append(
                store_data["locationType"]
                if store_data["locationType"]
                else "<MISSING>"
            )
            store.append(lat)
            store.append(lng)
            hours = ""
            if "monopen" in store_data and store_data["monopen"] is not None:
                hours = (
                    hours
                    + " monday "
                    + store_data["monopen"]
                    + " - "
                    + store_data["monclose"]
                )
            if "tuesopen" in store_data and store_data["tuesopen"] is not None:
                hours = (
                    hours
                    + " tuesday "
                    + store_data["tuesopen"]
                    + " - "
                    + store_data["tuesclose"]
                )
            if "wedopen" in store_data and store_data["wedopen"] is not None:
                hours = (
                    hours
                    + " wednesda "
                    + store_data["wedopen"]
                    + " - "
                    + store_data["wedclose"]
                )
            if "thuopen" in store_data and store_data["thuopen"] is not None:
                hours = (
                    hours
                    + " thursday "
                    + store_data["thuopen"]
                    + " - "
                    + store_data["thuclose"]
                )
            if "friopen" in store_data and store_data["friopen"] is not None:
                hours = (
                    hours
                    + " friday "
                    + store_data["friopen"]
                    + " - "
                    + store_data["friclose"]
                )
            if "satopen" in store_data and store_data["satopen"] is not None:
                hours = (
                    hours
                    + " saturday "
                    + store_data["satopen"]
                    + " - "
                    + store_data["satclose"]
                )
            if "sunopen" in store_data and store_data["sunopen"] is not None:
                hours = (
                    hours
                    + " sunday "
                    + store_data["sunopen"]
                    + " - "
                    + store_data["satclose"]
                )
            store.append(hours if hours != "" else "<MISSING>")
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
