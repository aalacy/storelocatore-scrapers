import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
import json

logger = SgLogSetup().get_logger("goodwill_org")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_radius_miles=5,
    max_search_results=10,
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
    sids = []
    for lat, lng in search:
        llat = lat
        llng = lng
        logger.info("%s-%s..." % (llat, llng))
        url = (
            "https://www.goodwill.org/GetLocAPI.php?lat="
            + str(llat)
            + "&lng="
            + str(llng)
            + "&cats=3%2C1%2C2%2C4%2C6%2C7%2C5"
        )
        try:
            r = session.get(url, headers=headers)
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
                if phone == "":
                    phone = "<MISSING>"
                loc = item["LocationParentWebsite"]
                if phone == "":
                    phone = "<MISSING>"
                if "." not in loc:
                    loc = "<MISSING>"
                hours = "<MISSING>"
                try:
                    if "-" not in phone:
                        phone = "<MISSING>"
                except:
                    phone = "<MISSING>"
                if store not in sids:
                    if (
                        state == "ON"
                        or state == "QC"
                        or state == "PE"
                        or state == "NB"
                        or state == "NS"
                        or state == "AB"
                        or state == "PEI"
                        or state == "BC"
                        or state == "SK"
                        or state == "Alberta"
                        or state == "Quebec"
                        or state == "Ontario"
                    ):
                        country = "CA"
                    if (
                        "1495 Sneed Rd" not in add
                        and "2714 Fairview Blvd" not in add
                        and "3812 Hillsboro Rd" not in add
                    ):
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
        except:
            pass


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
