import csv
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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
    addressess = []
    coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=200,
        max_search_results=75,
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
    }
    base_url = "https://carpetspluscolortile.com/"

    for cord in coords:

        page_api = (
            "https://carpetspluscolortile.com/wp-admin/admin-ajax.php?action=store_search&lat="
            + str(cord[0])
            + "&lng="
            + str(cord[1])
            + "&max_results=100&search_radius=500"
        )
        json_data = session.post(page_api, headers=headers).json()

        for value in json_data:
            name = value["store"]
            address = value["address"]
            city = value["city"]
            state = value["state"]
            zip = value["zip"]
            store_number = value["id"]
            phone = value["phone"]
            latitude = value["lat"]
            longitude = value["lng"]
            page_url = value["url"]

            store = []
            store.append(base_url)
            store.append(name)
            store.append(address)
            store.append(city)
            store.append(state)
            store.append(zip)
            store.append("US")
            store.append(store_number)
            store.append(phone)
            store.append("CarpetsPlus COLORTILE retailer")
            store.append(latitude)
            store.append(longitude)
            store.append("<MISSING>")
            store.append(page_url if page_url else "<MISSING>")

            if store[2] in addressess:
                continue
            addressess.append(store[2])

            yield store


def scrape():

    data = fetch_data()
    write_output(data)


scrape()
