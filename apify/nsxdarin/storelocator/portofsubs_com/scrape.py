import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-olo-app-platform": "web",
    "x-olo-request": "1",
    "x-olo-viewport": "Desktop",
    "x-requested-with": "XMLHttpRequest",
}

logger = SgLogSetup().get_logger("portofsubs_com")


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
    url = "https://order.portofsubs.com/api/vendors/regions?excludeCities=true"
    r = session.get(url, headers=headers)
    website = "portofsubs.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    states = []
    for item in json.loads(r.content):
        states.append(item["code"])
    for state in states:
        surl = "https://order.portofsubs.com/api/vendors/search/" + state
        r2 = session.get(surl, headers=headers)
        logger.info(state)
        for item in json.loads(r2.content)["vendor-search-results"]:
            name = item["name"]
            loc = "https://order.portofsubs.com/menu/" + item["slug"]
            store = name.split("#")[1].strip()
            phone = item["phoneNumber"]
            add = item["address"]["streetAddress"]
            city = item["address"]["city"]
            state = item["address"]["state"]
            zc = item["address"]["postalCode"]
            lat = item["latitude"]
            lng = item["longitude"]
            hours = item["weeklySchedule"]["calendars"][0]["schedule"]
            hours = str(hours)
            allhours = ""
            days = hours.split("{'weekDay': '")
            for day in days:
                if "'description': '" in day:
                    hrs = (
                        day.split("'")[0]
                        + ": "
                        + day.split("'description': '")[1].split("'")[0]
                    )
                    if allhours == "":
                        allhours = hrs
                    else:
                        allhours = allhours + "; " + hrs
            if " (online" in name:
                name = name.split(" (online")[0]
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
                allhours,
            ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
