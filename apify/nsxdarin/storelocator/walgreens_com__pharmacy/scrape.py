import csv
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("walgreens_com__pharmacy")


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


search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_radius_miles=50,
    max_search_results=250,
)

session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
    "content-type": "application/json; charset=UTF-8",
}


def fetch_data():
    ids = []
    for code in search:
        try:
            logger.info(("Pulling Postal Code %s..." % code))
            url = "https://www.walgreens.com/locator/v1/stores/search?requestor=search"
            payload = {
                "r": "250",
                "requestType": "dotcom",
                "s": "100",
                "p": 1,
                "q": code,
                "lat": "",
                "lng": "",
                "zip": code,
            }
            r = session.post(url, headers=headers, data=json.dumps(payload))
            website = "walgreens.com/pharmacy"
            for item in json.loads(r.content)["results"]:
                loc = "https://www.walgreens.com" + item["storeSeoUrl"]
                store = loc.split("/id=")[1]
                lat = item["latitude"]
                country = "US"
                lng = item["longitude"]
                add = item["store"]["address"]["street"]
                zc = item["store"]["address"]["zip"]
                city = item["store"]["address"]["city"]
                state = item["store"]["address"]["state"]
                name = item["store"]["name"]
                hours = ""
                typ = "<MISSING>"
                Closed = False
                if store not in ids:
                    r2 = session.get(loc, headers=headers)
                    logger.info(loc)
                    for line2 in r2.iter_lines():
                        line2 = str(line2.decode("utf-8"))
                        if "This location is temporarily closed" in line2:
                            Closed = True
                        if "Pharmacy</strong></h3>" in line2 and hours == "":
                            days = (
                                line2.split("Pharmacy</strong></h3>")[1]
                                .split("</ul></li><li")[0]
                                .split('<li class="day"')
                            )
                            for day in days:
                                if "pharmacyHoursList" not in day:
                                    if ">Closed<" in day:
                                        hrs = (
                                            day.split(">")[1].split("<")[0] + ": Closed"
                                        )
                                    else:
                                        hrs = (
                                            day.split(">")[1].split("<")[0]
                                            + ": "
                                            + day.split("react-text:")[1]
                                            .split(">")[1]
                                            .split("<")[0]
                                        )
                                        hrs = (
                                            hrs
                                            + "-"
                                            + day.split("react-text:")[3]
                                            .split(">")[1]
                                            .split("<")[0]
                                        )
                                    if hours == "":
                                        hours = hrs
                                    else:
                                        hours = hours + "; " + hrs
                        if (
                            "Store &amp; Shopping</strong></h3>" in line2
                            and hours == ""
                        ):
                            days = (
                                line2.split("Store &amp; Shopping")[1]
                                .split("</ul></li><")[0]
                                .split('<li class="day"')
                            )
                            for day in days:
                                if "pharmacyHoursList" not in day:
                                    if ">Closed<" in day:
                                        hrs = (
                                            day.split(">")[1].split("<")[0] + ": Closed"
                                        )
                                    else:
                                        hrs = (
                                            day.split(">")[1].split("<")[0]
                                            + ": "
                                            + day.split("react-text:")[1]
                                            .split(">")[1]
                                            .split("<")[0]
                                        )
                                        hrs = (
                                            hrs
                                            + "-"
                                            + day.split("react-text:")[3]
                                            .split(">")[1]
                                            .split("<")[0]
                                        )
                                    if hours == "":
                                        hours = hrs
                                    else:
                                        hours = hours + "; " + hrs
                phone = (
                    item["store"]["phone"]["areaCode"]
                    + item["store"]["phone"]["number"]
                )
                if Closed:
                    hours = "Temporarily Closed"
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
        except:
            pass


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
