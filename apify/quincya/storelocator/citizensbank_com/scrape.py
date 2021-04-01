import csv
import datetime
import json

from bs4 import BeautifulSoup

from sglogging import sglog

from sgrequests import SgRequests

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="citizensbank.com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    found_poi = []

    max_results = None
    max_distance = 200

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=max_distance,
        max_search_results=max_results,
    )

    date_str = str(datetime.date.today())

    for lat, lng in search:
        log.info(
            "Searching: %s, %s | Items remaining: %s"
            % (lat, lng, search.items_remaining())
        )
        base_link = (
            "https://www.citizensbank.com/apps/ApiProxy/BranchlocatorApi/api/BranchLocator?RequestHeader%5BRqStartTime%5D="
            + date_str
            + "&coordinates%5BLatitude%5D="
            + str(lat)
            + "&coordinates%5BLongitude%5D="
            + str(lng)
            + "&searchFilter%5BIncludeAtms%5D=false&searchFilter%5BIncludeBranches%5D=true&searchFilter%5BIncludeVoiceAssistedAtms%5D=false&searchFilter%5BIncludeSuperMarketBranches%5D=true&searchFilter%5BIncludeOpenNow%5D=false&searchFilter%5BRadius%5D="
            + str(max_distance)
        )
        req = session.get(base_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        items = json.loads(base.text)["BranchCollection"]
        for item in items:

            locator_domain = "citizensbank.com"
            if item["IsBranch"] == "False":
                continue
            street_address = (
                item["Address"]["StreetAddress"]["Value"]
                .replace("Cambridge MA", "")
                .replace("  ", " ")
                .strip()
            )
            if street_address[-1:] == ",":
                street_address = street_address[:-1]
            location_name = item["BranchName"]["Value"]
            city = item["Address"]["City"]
            state = item["Address"]["State"]
            zip_code = item["Address"]["Zip"].replace(".", "")
            country_code = "US"
            store_number = item["BranchId"]
            if store_number in found_poi:
                continue
            found_poi.append(store_number)
            phone = item["Address"]["Phone"]
            location_type = "<MISSING>"
            hours_of_operation = item["LobbyHours"]["Description"].replace(
                "na", "Closed"
            )
            latitude = item["Address"]["Coordinates"]["Latitude"]
            longitude = item["Address"]["Coordinates"]["Longitude"]

            search.found_location_at(latitude, longitude)

            link = "https://www.citizensbank.com/customer-service/branch-locator.aspx"

            yield [
                    locator_domain,
                    link,
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

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
