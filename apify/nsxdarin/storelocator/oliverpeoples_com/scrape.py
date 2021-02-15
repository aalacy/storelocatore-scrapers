import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "Ocp-Apim-Subscription-Key": "20196d3dd300423db799b08190bc27e2",
}

logger = SgLogSetup().get_logger("oliverpeoples_com")


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
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=50,
        max_search_results=None,
    )
    for lat, lng in search:
        logger.info(str(lat) + "-" + str(lng) + "...")
        url = (
            "https://api-tab.luxottica.com/tl-store-locator/api/v1/OP/offices?latitude="
            + str(lat)
            + "&longitude="
            + str(lng)
            + "&radius=50&limit=20&offset=0&uom=KM&officeTypes=BOUTIQUE"
        )
        r = session.get(url, headers=headers)
        website = "oliverpeoples.com"
        typ = "Hospital"
        logger.info("Pulling Stores")
        for item in json.loads(r.content)["records"]:
            hours = ""
            country = item["address"]["country"]
            add = item["address"]["address"]
            city = item["address"]["city"]
            state = item["address"]["state"]
            zc = item["address"]["postalCode"]
            lat = item["latitude"]
            lng = item["longitude"]
            try:
                loc = "https://www.oliverpeoples.com/usa" + item["url"]
            except:
                loc = "<MISSING>"
            store = item["storeNumber"]
            phone = item["phone"]
            name = item["name"]
            typ = item["officeType"]
            for day in item["officeHours"]:
                try:
                    hrs = (
                        day["dayOfWeek"] + ": " + day["opening"] + "-" + day["closing"]
                    )
                except:
                    hrs = day["dayOfWeek"] + ": Closed"
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if phone == "" or phone is None:
                phone = "<MISSING>"
            if hours == "":
                hours = "<MISSING>"
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
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA],
        max_radius_miles=50,
        max_search_results=None,
    )
    for lat, lng in search:
        logger.info(str(lat) + "-" + str(lng) + "...")
        url = (
            "https://api-tab.luxottica.com/tl-store-locator/api/v1/OP/offices?latitude="
            + str(lat)
            + "&longitude="
            + str(lng)
            + "&radius=50&limit=20&offset=0&uom=KM&officeTypes=BOUTIQUE"
        )
        r = session.get(url, headers=headers)
        website = "oliverpeoples.com"
        typ = "<MISSING>"
        country = "CA"
        logger.info("Pulling Stores")
        for item in json.loads(r.content)["records"]:
            hours = ""
            country = item["address"]["country"]
            add = item["address"]["address"]
            city = item["address"]["city"]
            state = item["address"]["state"]
            zc = item["address"]["postalCode"]
            lat = item["latitude"]
            lng = item["longitude"]
            try:
                loc = "https://www.oliverpeoples.com/usa" + item["url"]
            except:
                loc = "<MISSING>"
            store = item["storeNumber"]
            phone = item["phone"]
            name = item["name"]
            typ = item["officeType"]
            for day in item["officeHours"]:
                try:
                    hrs = (
                        day["dayOfWeek"] + ": " + day["opening"] + "-" + day["closing"]
                    )
                except:
                    hrs = day["dayOfWeek"] + ": Closed"
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if phone == "" or phone is None:
                phone = "<MISSING>"
            if hours == "":
                hours = "<MISSING>"
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
