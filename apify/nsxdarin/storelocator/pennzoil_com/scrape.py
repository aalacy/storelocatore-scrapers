import csv
from sgrequests import SgRequests
import json
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("pennzoil_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=50,
    max_search_results=5,
)


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
    locations = []
    for lat, lng in search:
        try:
            x = lat
            y = lng
            logger.info(str(x) + "," + str(y))
            website = "pennzoil.com"
            url = (
                "https://locator.pennzoil.com/api/v1/pennzoil/oil_change_locations/nearest_to?limit=50&lat="
                + str(x)
                + "&lng="
                + str(y)
                + "&format=json"
            )
            r = session.get(url, headers=headers, timeout=15)
            purl = "<MISSING>"
            for item in json.loads(r.content):
                store = item["id"]
                name = item["name"]
                lat = item["lat"]
                lng = item["lng"]
                add = item["address1"]
                city = item["city"]
                state = item["state"]
                zc = item["postcode"]
                country = "US"
                phone = item["telephone"]
                if phone == "":
                    phone = "<MISSING>"
                hours = "<MISSING>"
                typ = "<MISSING>"
                canada = [
                    "NL",
                    "NS",
                    "PE",
                    "QC",
                    "ON",
                    "BC",
                    "AB",
                    "MB",
                    "SK",
                    "YT",
                    "NU",
                    "NT",
                    "NB",
                ]
                if store not in locations and state not in canada:
                    locations.append(store)
                    if "PENNZOIL" in name.upper():
                        yield [
                            website,
                            purl,
                            name,
                            add,
                            city,
                            state,
                            zc,
                            country,
                            store,
                            phone,
                            typ,
                            lat,
                            lng,
                            hours,
                        ]
        except:
            pass


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
