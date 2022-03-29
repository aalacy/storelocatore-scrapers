import csv
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("watermillexpress_com")


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
    addresses = []
    coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=25,
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }

    base_url = "http://www.watermillexpress.com"

    for lat, lng in coords:

        location_url = (
            "https://watermillexpress.com/wp-admin/admin-ajax.php?action=store_search&lat="
            + str(lat)
            + "&lng="
            + str(lng)
            + "&max_results=25&search_radius=25&search=&statistics="
        )
        try:
            r_locations = session.get(location_url, headers=headers)
            json_data = r_locations.json()
        except:
            continue

        locator_domain = base_url
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "US"
        store_number = ""
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        hours_of_operation = "<MISSING>"
        page_url = (
            "http://www.watermillexpress.com/wp-admin/admin-ajax.php?action=store_search&lat="
            + str(lat)
            + "&lng="
            + str(lng)
            + "&max_results=25&search_radius=25&search=&statistics="
        )

        for location in json_data:
            city = location["city"]
            state = location["state"]
            zipp = location["zip"]
            address2 = location["address2"]
            street_address = (
                location["address"] + " " + str(address2).replace("None", "")
            )
            latitude = location["lat"]
            longitude = location["lng"]
            phone = location["phone"]
            store_number = location["store"]
            page_url = "<MISSING>"
            hours_of_operation = "Open 24/7"

            store = [
                locator_domain,
                location_name,
                street_address,
                city,
                state,
                zipp,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
                page_url,
            ]

            if str(store[2] + str(store[8] + str(store[7]))) in addresses:
                continue
            addresses.append(str(store[2] + str(store[8]) + str(store[7])))
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
