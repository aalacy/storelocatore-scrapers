import csv
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("harborfreight_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_radius_miles=50,
    max_search_results=None,
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
    ids = []
    typ = "<MISSING>"
    website = "harborfreight.com"
    for lat, lng in search:
        logger.info(str(lat) + "-" + str(lng))
        url = (
            "https://www.harborfreight.com/api/storelocator/location_api/page?lat="
            + str(lat)
            + "&lng="
            + str(lng)
        )
        r = session.get(url, headers=headers)
        for item in json.loads(r.content)["data"]["stores"]:
            store = item["number"]
            loc = "https://www.harborfreight.com/storelocator/store?number=" + store
            name = item["name"]
            country = "US"
            add = item["address"]
            city = item["city"]
            state = item["state"]
            zc = item["zip"]
            phone = item["phone"]
            lat = item["latitude"]
            lng = item["longitude"]
            hours = (
                str(item["open_hours"])
                .replace("', '", "; ")
                .replace("'", "")
                .replace("{", "")
                .replace("}", "")
                .strip()
            )
            status = item["status"]
            if store not in ids:
                if status == "NEW" or status == "OPEN":
                    ids.append(store)
                    if add == "":
                        add = "<MISSING>"
                    yield [
                        website,
                        loc,
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


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
