import csv
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("bankofamerica_com__atm")


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
    max_radius_miles=None,
    max_search_results=50,
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
            "https://maps.bankofamerica.com/api/getAsyncLocations?template=search&level=search&search="
            + zipcode
        )
        r = session.get(url, headers=headers)
        website = "bankofamerica.com/atm"
        typ = "ATM"
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '{"lat":"' in line:
                items = line.split('{"lat":"')
                for item in items:
                    if '"lng":"' in item:
                        country = "US"
                        lat = item.split('"')[0]
                        lng = item.split('"lng":"')[1].split('"')[0]
                        store = item.split('"locationId":"')[1].split('"')[0]
                        add = item.split("\\u0022address_1\\u0022: \\u0022")[1].split(
                            "\\u"
                        )[0]
                        city = item.split("\\u0022city\\u0022: \\u0022")[1].split(
                            "\\u"
                        )[0]
                        state = item.split("\\u0022region\\u0022: \\u0022")[1].split(
                            "\\u"
                        )[0]
                        zc = item.split("\\u0022post_code\\u0022: \\u0022")[1].split(
                            "\\u"
                        )[0]
                        hours = "<MISSING>"
                        phone = "<MISSING>"
                        loc = (
                            item.split("\\u0022url\\u0022: \\u0022")[1]
                            .split("\\u")[0]
                            .replace("\\", "")
                        )
                        name = item.split("location_name\\u0022: \\u0022")[1].split(
                            "\\u"
                        )[0]
                        if store not in ids and '"group":"ATM Services' in item:
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
