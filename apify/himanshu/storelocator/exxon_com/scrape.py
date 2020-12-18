import csv
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("exxon_com")


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=25,
        max_search_results=250,
    )

    addresses = []

    for lat, long in search:

        result_coords = []

        base_url = (
            "https://www.exxon.com/en/api/locator/Locations?Latitude1="
            + str(lat)
            + "&Latitude2="
            + str(lat + 1)
            + "&Longitude1="
            + str(long)
            + "&Longitude2="
            + str(long + 1)
            + "&DataSource=RetailGasStations&Country=US"
        )

        r = session.get(base_url).json()

        for location in r:

            if "MOBIL" in location["DisplayName"]:
                continue
            if "Mobil" in location["DisplayName"]:
                continue
            if "mobil" in location["BrandingImage"]:
                continue
            page_url = (
                "https://www.exxon.com/en/find-station/"
                + location["City"].lower().replace(" ", "").strip()
                + "-"
                + location["StateProvince"].lower().strip()
                + "-"
                + location["DisplayName"]
                .lower()
                .replace(" ", "")
                .replace("#", "-")
                .strip()
                + "-"
                + location["LocationID"].strip()
            )
            result_coords.append((location["Latitude"], location["Longitude"]))

            store = []
            store.append("https://www.exxon.com")
            store.append(location["DisplayName"].strip())
            store.append(location["AddressLine1"].strip())
            store.append(location["City"].strip())
            store.append(location["StateProvince"].strip())
            store.append(location["PostalCode"].strip())
            if location["Country"] == "United States":
                store.append("US")
            else:
                store.append(location["Country"])
            store.append(location["LocationID"].strip())
            if location["Telephone"]:
                store.append(location["Telephone"].strip())
            else:
                store.append("<MISSING>")
            store.append("exxon")
            store.append(location["Latitude"])
            store.append(location["Longitude"])
            if location["WeeklyOperatingHours"]:
                store.append(location["WeeklyOperatingHours"].replace("<br/>", ","))
            else:
                store.append("<MISSING>")
            store.append(page_url)
            if (str(store[2]) + str(store[-1])) in addresses:
                continue
            addresses.append(str(store[2]) + str(store[-1]))
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
