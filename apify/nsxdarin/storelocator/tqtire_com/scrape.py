import csv
from sgrequests import SgRequests
import json
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("tqtire_com")

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_radius_miles=50,
    max_search_results=20,
)

session = SgRequests()
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
        x = lat
        y = lng
        url = (
            "https://www.tqtire.com/wp-json/monro/v1/stores/coords?latitude="
            + str(x)
            + "&longitude="
            + str(y)
            + "&distance=50"
        )
        logger.info("%s - %s..." % (str(x), str(y)))
        website = "tqtire.com"
        country = "US"
        r = session.get(url, headers=headers)
        if '{"Id":' in r.content.decode("utf-8"):
            for item in json.loads(r.content)["data"]:
                store = item["Id"]
                typ = item["BrandId"]
                name = item["BrandDisplayName"]
                add = item["Address"] + " " + item["Address2"]
                add = add.strip()
                city = item["City"]
                zc = item["ZipCode"]
                state = item["StateCode"]
                lat = item["Latitude"]
                loc = "<MISSING>"
                lng = item["Longitude"]
                hours = "Sun: " + item["SundayOpenTime"] + "-" + item["SundayCloseTime"]
                hours = (
                    hours
                    + "; Mon: "
                    + item["MondayOpenTime"]
                    + "-"
                    + item["MondayCloseTime"]
                )
                hours = (
                    hours
                    + "; Tue: "
                    + item["TuesdayOpenTime"]
                    + "-"
                    + item["TuesdayCloseTime"]
                )
                hours = (
                    hours
                    + "; Wed: "
                    + item["WednesdayOpenTime"]
                    + "-"
                    + item["WednesdayCloseTime"]
                )
                hours = (
                    hours
                    + "; Thu: "
                    + item["ThursdayOpenTime"]
                    + "-"
                    + item["ThursdayCloseTime"]
                )
                hours = (
                    hours
                    + "; Fri: "
                    + item["FridayOpenTime"]
                    + "-"
                    + item["FridayCloseTime"]
                )
                hours = (
                    hours
                    + "; Sat: "
                    + item["SaturdayOpenTime"]
                    + "-"
                    + item["SaturdayCloseTime"]
                )
                hours = hours.replace("00:00:00-00:00:00", "Closed")
                hours = hours.replace(":00-", "-")
                hours = hours.replace(":00;", ";")
                hours = hours.replace(":00:00", ":00")
                hours = hours.replace(":30:00", ":30")
                phone = item["SalesPhone"]
                if zc == "":
                    zc = "<MISSING>"
                if hours == "":
                    hours = "<MISSING>"
                if phone == "":
                    phone = "<MISSING>"
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
