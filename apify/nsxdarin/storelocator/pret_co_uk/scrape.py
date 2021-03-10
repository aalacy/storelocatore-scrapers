import csv
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("pret_co_uk")


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
    country_codes=[SearchableCountries.BRITAIN],
    max_radius_miles=None,
    max_search_results=20,
)

session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
    "Cookie": "statePreference=; statePreference=; preferredLocal=city=&countrycode=UK, GB&latitude=0&longitude=0; PretAManger-UK_Language=en-gb; _ga=GA1.3.682867871.1588958973; _gid=GA1.3.711697636.1588958973; _fbp=fb.2.1588958973219.1726351087; _y2=1%3AeyJjIjp7IjEyNDc2NiI6LTE0NzM5ODQwMDAsIjEyNTIxOCI6LTE0NzM5ODQwMDAsIjEyOTQ4NiI6LTE0NzM5ODQwMDAsIjEzMDIxNiI6LTE0NzM5ODQwMDAsIjEzMTc5NCI6LTE0NzM5ODQwMDAsIjEzMjUwOSI6LTE0NzM5ODQwMDAsIm8iOi0xNDczOTg0MDAwfX0%3D%3ALTE0NzEzNjMxNjg%3D%3A99; newsletterPageReferrer=https://www.pret.co.uk/en-gb/find-a-pret/London; OptanonConsent=isIABGlobal=false&datestamp=Fri+May+08+2020+12%3A30%3A37+GMT-0500+(Central+Daylight+Time)&version=5.9.0&landingPath=NotLandingPage&groups=1%3A1%2C2%3A1%2C3%3A1%2C4%3A1%2C0_48371%3A1%2C0_48370%3A1%2C0_94508%3A1%2C0_94507%3A1%2C0_48372%3A1%2C0_48365%3A1%2C0_48367%3A1%2C0_48366%3A1%2C0_48369%3A1%2C0_48368%3A1%2C8%3A0&AwaitingReconsent=false; newsletterAction=dwell; newsletterDwellTime=56; _yi=1%3AeyJsaSI6bnVsbCwic2UiOnsiYyI6MSwibGEiOjE1ODg5NTkxMjEzNzgsInAiOjUsInNjIjoxMjN9LCJ1Ijp7ImlkIjoiZDA1MDIzNTctZWYxZC00OTlhLThmODAtOWIxMmI5MzVkYmVjIiwiZmwiOiIwIn19%3ALTE0MzE4NDYxMTI%3D%3A99; lastTimestamp=1588959122; preferredLocal=city=&countrycode=UK, GB&latitude=0&longitude=0; PretAManger-UK_Language=en-gb",
}


def fetch_data():
    ids = []
    for zipcode in search:
        logger.info(("Pulling Postal Code %s..." % zipcode))
        url = (
            "https://www.pret.co.uk/api/stores/by-address?address="
            + zipcode
            + "&market=UK"
        )
        r = session.get(url, headers=headers)
        try:
            for item in json.loads(r.content):
                website = "pret.co.uk"
                loc = "<MISSING>"
                country = "GB"
                store = item["id"]
                name = item["name"]
                lat = item["location"]["lat"]
                lng = item["location"]["lng"]
                add = item["address"]["streetNumber"]
                try:
                    add = add + " " + item["address"]["streetName"]
                except:
                    pass
                city = item["address"]["city"]
                state = "<MISSING>"
                zc = item["address"]["postalCode"]
                phone = item["contact"]["phone"]
                typ = item["features"]["storeType"]
                hours = (
                    "Sun: "
                    + str(item["tradingHours"][0][0])
                    + "-"
                    + str(item["tradingHours"][0][1])
                )
                hours = (
                    hours
                    + "; Mon: "
                    + str(item["tradingHours"][1][0])
                    + "-"
                    + str(item["tradingHours"][1][1])
                )
                hours = (
                    hours
                    + "; Tue: "
                    + str(item["tradingHours"][2][0])
                    + "-"
                    + str(item["tradingHours"][2][1])
                )
                hours = (
                    hours
                    + "; Wed: "
                    + str(item["tradingHours"][3][0])
                    + "-"
                    + str(item["tradingHours"][3][1])
                )
                hours = (
                    hours
                    + "; Thu: "
                    + str(item["tradingHours"][4][0])
                    + "-"
                    + str(item["tradingHours"][4][1])
                )
                hours = (
                    hours
                    + "; Fri: "
                    + str(item["tradingHours"][5][0])
                    + "-"
                    + str(item["tradingHours"][5][1])
                )
                hours = (
                    hours
                    + "; Sat: "
                    + str(item["tradingHours"][6][0])
                    + "-"
                    + str(item["tradingHours"][6][1])
                )
                hours = hours.replace("00:00-00:00", "Closed")
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
