import csv
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("hobbs_co_uk")

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
            "https://www.hobbs.com/on/demandware.store/Sites-HB-UK-Site/en/Stores-FindStores?lat="
            + str(x)
            + "&long="
            + str(y)
            + "&dwfrm_address_country=GB"
        )
        logger.info("%s - %s..." % (str(x), str(y)))
        website = "hobbs.co.uk"
        r = session.get(url, headers=headers)
        for item in json.loads(r.content)["stores"]:
            store = item["ID"]
            name = item["name"]
            add = item["address1"]
            try:
                add = add + " " + item["address2"]
            except:
                pass
            city = item["city"]
            state = "<MISSING>"
            zc = item["postalCode"]
            if zc == "" or zc is None:
                zc = "<MISSING>"
            lat = item["latitude"]
            lng = item["longitude"]
            try:
                phone = item["phone"]
            except:
                phone = "<MISSING>"
            country = item["countryCode"]
            typ = item["storeType"]
            if city == "" or city is None:
                city = "<MISSING>"
            hours = ""
            loc = "https://www.hobbs.com" + item["storeUrl"]
            for day in item["workTimes"]:
                hrs = day["weekDay"] + ": " + day["value"]
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
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
