import csv
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

session = SgRequests()
headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
}

logger = SgLogSetup().get_logger("kellyservices_com")

search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_radius_miles=25,
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
    url = "https://www.kellyservices.us/api/branchlocator/search"
    ids = []
    for zipcode in search:
        try:
            logger.info(("Pulling Postal Code %s..." % zipcode))
            payload = {"zipcodes": zipcode, "state": "", "city": ""}
            r = session.post(url, headers=headers, data=json.dumps(payload))
            website = "kellyservices.com"
            typ = "Branch"
            for item in json.loads(r.content)["rows"]:
                store = item["unitId"]
                loc = "<MISSING>"
                name = item["unitName"]
                add = item["addressLine1"]
                try:
                    add = add + " " + item["addressLine2"]
                except:
                    pass
                add = add.strip()
                city = item["city"]
                state = item["stateProvinceCode"]
                zc = item["postalCode"]
                country = item["country"]
                if country == "USA":
                    country = "US"
                else:
                    country = "CA"
                phone = item["phoneNumber"]
                lat = item["latitude"]
                lng = item["longitude"]
                hours = "<MISSING>"
                if phone == "" or phone is None:
                    phone = "<MISSING>"
                if store not in ids and store != "":
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
        except:
            pass


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
