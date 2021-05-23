import csv
from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("boostmobile_com")

search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_radius_miles=None,
    max_search_results=50,
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
    for coord in search:
        try:
            logger.info(coord)
            url = (
                "https://boostmobile.nearestoutlet.com/cgi-bin/jsonsearch-cs.pl?showCaseInd=false&brandId=bst&results=50&zipcode="
                + coord
                + "&page=1"
            )
            r = session.get(url, headers=headers)
            array = json.loads(r.content)
            count = int(array["nearestOutletResponse"]["resultsFoundNum"])
            pages = int((count - 1) / 50) + 2
            for x in range(1, pages):
                url = (
                    "https://boostmobile.nearestoutlet.com/cgi-bin/jsonsearch-cs.pl?showCaseInd=false&brandId=bst&results=50&zipcode="
                    + coord
                    + "&page="
                    + str(x)
                )
                r = session.get(url, headers=headers)
                array = json.loads(r.content)
                for item in array["nearestOutletResponse"]["nearestlocationinfolist"][
                    "nearestLocationInfo"
                ]:
                    website = "boostmobile.com"
                    store = item["id"]
                    name = "Boost Mobile"
                    typ = item["storeName"]
                    add = item["storeAddress"]["primaryAddressLine"]
                    city = item["storeAddress"]["city"]
                    state = item["storeAddress"]["state"]
                    zc = item["storeAddress"]["zipCode"]
                    lat = item["storeAddress"]["lat"]
                    lng = item["storeAddress"]["long"]
                    country = "US"
                    phone = item["storePhone"]
                    loc = item["elevateURL"]
                    hours = "Mon: " + item["storeHours"]["mon"]
                    hours = hours + "; Tue: " + item["storeHours"]["tue"]
                    hours = hours + "; Wed: " + item["storeHours"]["wed"]
                    hours = hours + "; Thu: " + item["storeHours"]["thu"]
                    hours = hours + "; Fri: " + item["storeHours"]["fri"]
                    hours = hours + "; Sat: " + item["storeHours"]["sat"]
                    hours = hours + "; Sun: " + item["storeHours"]["sun"]
                    if lat == "":
                        lat = "<MISSING>"
                    if lng == "":
                        lng = "<MISSING>"
                    if phone == "":
                        phone = "<MISSING>"
                    if "see store" in hours.lower():
                        hours = "<MISSING>"
                    storeinfo = add + "|" + city + "|" + state
                    if loc == "" or loc is None:
                        loc = "<MISSING>"
                    if storeinfo not in ids and store != "" and "Boost Mobile" in typ:
                        ids.append(storeinfo)
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
