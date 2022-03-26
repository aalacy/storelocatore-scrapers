import csv
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("huntington_com__atm")

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=None,
    max_search_results=10,
)


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
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
        try:
            x = lat
            y = lng
            url = "https://www.huntington.com/post/GetLocations/GetLocationsList"
            payload = {
                "longitude": lng,
                "latitude": lat,
                "typeFilter": "2",
                "envelopeFreeDepositsFilter": False,
                "timeZoneOffset": "300",
                "scController": "GetLocations",
                "scAction": "GetLocationsList",
            }
            logger.info("%s - %s..." % (str(x), str(y)))
            session = SgRequests()
            r = session.post(url, headers=headers, data=payload)
            for item in json.loads(r.content)["features"]:
                store = item["properties"]["LocID"]
                name = item["properties"]["LocName"]
                add = item["properties"]["LocStreet"]
                phone = item["properties"]["LocPhone"]
                city = item["properties"]["LocCity"]
                state = item["properties"]["LocState"]
                zc = item["properties"]["LocZip"]
                typ = "ATM"
                website = "huntington.com/atm"
                country = "US"
                lat = item["geometry"]["coordinates"][0]
                lng = item["geometry"]["coordinates"][1]
                search.found_location_at(lng, lat)
                try:
                    hours = "Sun: " + item["properties"]["SundayLobbyHours"]
                    hours = hours + "; Mon: " + item["properties"]["MondayLobbyHours"]
                    hours = hours + "; Tue: " + item["properties"]["TuesdayLobbyHours"]
                    hours = (
                        hours + "; Wed: " + item["properties"]["WednesdayLobbyHours"]
                    )
                    hours = hours + "; Thu: " + item["properties"]["ThursdayLobbyHours"]
                    hours = hours + "; Fri: " + item["properties"]["FridayLobbyHours"]
                    hours = hours + "; Sat: " + item["properties"]["SaturdayLobbyHours"]
                except:
                    hours = "<MISSING>"
                storeinfo = store + "|" + add + "|" + typ + "|" + zc
                if storeinfo not in ids:
                    ids.append(storeinfo)
                    loc = "<MISSING>"
                    if phone == "":
                        phone = "<MISSING>"
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
            url = "https://www.huntington.com/post/GetLocations/GetLocationsList"
            lat = "39.96"
            lng = "-82.99879419999999"
            payload = {
                "longitude": lng,
                "latitude": lat,
                "typeFilter": "1",
                "envelopeFreeDepositsFilter": False,
                "timeZoneOffset": "300",
                "scController": "GetLocations",
                "scAction": "GetLocationsList",
            }
            logger.info("%s - %s..." % (str(x), str(y)))
            session = SgRequests()
            r = session.post(url, headers=headers, data=payload)
            for item in json.loads(r.content)["features"]:
                store = item["properties"]["LocID"]
                name = item["properties"]["LocName"]
                add = item["properties"]["LocStreet"]
                phone = item["properties"]["LocPhone"]
                city = item["properties"]["LocCity"]
                state = item["properties"]["LocState"]
                zc = item["properties"]["LocZip"]
                typ = "Branch"
                website = "huntington.com/atm"
                country = "US"
                lat = item["geometry"]["coordinates"][0]
                lng = item["geometry"]["coordinates"][1]
                DT = item["properties"]["DriveThruServices"]
                WU = item["properties"]["WalkUpATMServices"]
                IN = item["properties"]["InteriorATMServices"]
                BS = item["properties"]["BrandedATMServices"]
                search.found_location_at(lng, lat)
                try:
                    hours = "Sun: " + item["properties"]["SundayLobbyHours"]
                    hours = hours + "; Mon: " + item["properties"]["MondayLobbyHours"]
                    hours = hours + "; Tue: " + item["properties"]["TuesdayLobbyHours"]
                    hours = (
                        hours + "; Wed: " + item["properties"]["WednesdayLobbyHours"]
                    )
                    hours = hours + "; Thu: " + item["properties"]["ThursdayLobbyHours"]
                    hours = hours + "; Fri: " + item["properties"]["FridayLobbyHours"]
                    hours = hours + "; Sat: " + item["properties"]["SaturdayLobbyHours"]
                except:
                    hours = "<MISSING>"
                storeinfo = store + "|" + add + "|" + typ + "|" + zc
                if storeinfo not in ids:
                    ids.append(storeinfo)
                    if DT != "" or WU != "" or IN != "" or BS != "":
                        loc = (
                            "https://www.huntington.com/Community/branch-info?locationId="
                            + store.replace("bko", "")
                        )
                        if phone == "":
                            phone = "<MISSING>"
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
