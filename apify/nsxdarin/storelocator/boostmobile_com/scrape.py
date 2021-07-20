import csv
from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
}

logger = SgLogSetup().get_logger("boostmobile_com")

search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_radius_miles=None,
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
    for coord in search:

        logger.info(f"Zip Code: {coord}")
        url = (
            "https://boostmobile.nearestoutlet.com/cgi-bin/jsonsearch-cs.pl?showCaseInd=false&brandId=bst&results=50&zipcode="
            + coord
            + "&page=1"
        )
        r = session.get(url, headers=headers)
        try:
            array = json.loads(r.content, strict=False)
        except Exception:
            raise Exception(f"Err on this zip:{url}")
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
            try:
                array = json.loads(r.content, strict=False)
            except Exception:
                raise Exception(f"Err on this zip:{url}")
            for item in array["nearestOutletResponse"]["nearestlocationinfolist"][
                "nearestLocationInfo"
            ]:
                website = "boostmobile.com"
                store = item["id"]
                name = item["storeName"]  # Change Location Name as  we discussed
                typ = "Mobile Store"  # Change Location type as  we discussed
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
                if lat and lng:
                    search.found_location_at(lat, lng)
                    logger.info(f"found loc at ({lat}, {lng})")
                if lat == "":
                    lat = "<MISSING>"
                if lng == "":
                    lng = "<MISSING>"
                if phone == "":
                    phone = "<MISSING>"
                if "see store" in hours.lower():
                    hours = "<MISSING>"
                if loc == "" or loc is None:
                    loc = "<MISSING>"
                # store_number should be unique
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


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
