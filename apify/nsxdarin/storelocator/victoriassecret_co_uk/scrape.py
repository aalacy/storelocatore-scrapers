import csv
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("victoriassecret_co_uk")

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.BRITAIN],
    max_radius_miles=None,
    max_search_results=10,
)

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
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
    ids = []
    for lat, lng in search:
        x = lat
        y = lng
        url = (
            "https://api.victoriassecret.com/stores/v1/search/geolocation?latitude="
            + str(x)
            + "&longitude="
            + str(y)
            + "&variantId=undefined&activeCountry=GB"
        )
        logger.info("%s - %s..." % (str(x), str(y)))
        website = "victoriassecret.co.uk"
        r = session.get(url, headers=headers)
        for item in json.loads(r.content):
            store = item["storeId"]
            loc = "https://www.victoriassecret.com/gb/store-locator#store/" + store
            country = item["address"]["countryCode"]
            typ = "<MISSING>"
            name = item["name"]
            add = item["address"]["streetAddress1"]
            city = item["address"]["city"]
            state = item["address"]["region"]
            zc = item["address"]["postalCode"]
            phone = item["address"]["phone"]
            lat = item["latitudeDegrees"]
            lng = item["longitudeDegrees"]
            hours = "Sun: " + item["hours"][0]["open"] + "-" + item["hours"][0]["close"]
            hours = (
                hours
                + "; Mon: "
                + item["hours"][1]["open"]
                + "-"
                + item["hours"][1]["close"]
            )
            hours = (
                hours
                + "; Tue: "
                + item["hours"][2]["open"]
                + "-"
                + item["hours"][2]["close"]
            )
            hours = (
                hours
                + "; Wed: "
                + item["hours"][3]["open"]
                + "-"
                + item["hours"][3]["close"]
            )
            hours = (
                hours
                + "; Thu: "
                + item["hours"][4]["open"]
                + "-"
                + item["hours"][4]["close"]
            )
            hours = (
                hours
                + "; Fri: "
                + item["hours"][5]["open"]
                + "-"
                + item["hours"][5]["close"]
            )
            hours = (
                hours
                + "; Sat: "
                + item["hours"][6]["open"]
                + "-"
                + item["hours"][6]["close"]
            )
            hours = hours.replace("12:00 AM-12:00 AM", "Closed")
            if "0" not in hours:
                hours = "Temporarily Closed"
            if country == "GB":
                if store not in ids:
                    ids.append(store)
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
