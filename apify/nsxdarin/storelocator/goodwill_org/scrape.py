import csv
import sgzip
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("goodwill_org")

search = sgzip.ClosestNSearch()
search.initialize()

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

MAX_RESULTS = 10
MAX_DISTANCE = 5


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
    sids = []
    coord = search.next_coord()
    while coord:
        llat = coord[0]
        llng = coord[1]
        logger.info("%s-%s..." % (llat, llng))
        url = (
            "https://www.goodwill.org/GetLocAPI.php?lat="
            + str(llat)
            + "&lng="
            + str(llng)
            + "&cats=3%2C1%2C2%2C4%2C6%2C7%2C5"
        )
        r = session.get(url, headers=headers)
        array = []
        website = "goodwill.org"
        for item in json.loads(r.content):
            store = item["LocationId"]
            country = "US"
            typ = "<MISSING>"
            name = item["LocationName"]
            lat = item["LocationLatitude1"]
            lng = item["LocationLongitude1"]
            add = item["LocationStreetAddress1"]
            city = item["LocationCity1"]
            state = item["LocationState1"]
            zc = item["LocationPostal1"]
            phone = item["LocationPhoneOffice"]
            loc = item["LocationParentWebsite"]
            if phone == "":
                phone = "<MISSING>"
            hours = "<MISSING>"
            if store not in sids:
                sids.append(store)
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
        if len(array) <= MAX_RESULTS:
            logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
