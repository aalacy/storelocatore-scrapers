import csv
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgrequests import SgRequests
from sglogging import SgLogSetup
import time

logger = SgLogSetup().get_logger("bobcat_com")


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
    max_radius_miles=25,
    max_search_results=None,
)

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
    "Cookie": "statePreference=; statePreference=; preferredLocal=city=&countrycode=UK, GB&latitude=0&longitude=0; PretAManger-UK_Language=en-gb; _ga=GA1.3.682867871.1588958973; _gid=GA1.3.711697636.1588958973; _fbp=fb.2.1588958973219.1726351087; _y2=1%3AeyJjIjp7IjEyNDc2NiI6LTE0NzM5ODQwMDAsIjEyNTIxOCI6LTE0NzM5ODQwMDAsIjEyOTQ4NiI6LTE0NzM5ODQwMDAsIjEzMDIxNiI6LTE0NzM5ODQwMDAsIjEzMTc5NCI6LTE0NzM5ODQwMDAsIjEzMjUwOSI6LTE0NzM5ODQwMDAsIm8iOi0xNDczOTg0MDAwfX0%3D%3ALTE0NzEzNjMxNjg%3D%3A99; newsletterPageReferrer=https://www.pret.co.uk/en-gb/find-a-pret/London; OptanonConsent=isIABGlobal=false&datestamp=Fri+May+08+2020+12%3A30%3A37+GMT-0500+(Central+Daylight+Time)&version=5.9.0&landingPath=NotLandingPage&groups=1%3A1%2C2%3A1%2C3%3A1%2C4%3A1%2C0_48371%3A1%2C0_48370%3A1%2C0_94508%3A1%2C0_94507%3A1%2C0_48372%3A1%2C0_48365%3A1%2C0_48367%3A1%2C0_48366%3A1%2C0_48369%3A1%2C0_48368%3A1%2C8%3A0&AwaitingReconsent=false; newsletterAction=dwell; newsletterDwellTime=56; _yi=1%3AeyJsaSI6bnVsbCwic2UiOnsiYyI6MSwibGEiOjE1ODg5NTkxMjEzNzgsInAiOjUsInNjIjoxMjN9LCJ1Ijp7ImlkIjoiZDA1MDIzNTctZWYxZC00OTlhLThmODAtOWIxMmI5MzVkYmVjIiwiZmwiOiIwIn19%3ALTE0MzE4NDYxMTI%3D%3A99; lastTimestamp=1588959122; preferredLocal=city=&countrycode=UK, GB&latitude=0&longitude=0; PretAManger-UK_Language=en-gb",
}


def fetch_data():
    ids = []
    country = "US"
    for zipcode in search:
        typ = "<MISSING>"
        url = (
            "https://bobcat.know-where.com/bobcat/cgi/selection?option=T&option=R&option=E&option=M&option=G&option=W&option=X&option=U&option=P&option=V&option=D&place="
            + zipcode
            + "&lang=en&ll=&stype=place&async=results"
        )
        logger.info(("Pulling Postal Code %s..." % zipcode))
        session = SgRequests()
        time.sleep(2)
        r = session.get(url, headers=headers)
        lines = r.iter_lines()
        website = "bobcat.com"
        for line in lines:
            line = str(line.decode("utf-8"))
            if '<h4 style="margin: 0; color: black; font-size: 18px">' in line:
                name = line.split(
                    '<h4 style="margin: 0; color: black; font-size: 18px">'
                )[1].split("<")[0]
            if '<span onclick="">' in line:
                loc = "<MISSING>"
                g = next(lines)
                g = str(g.decode("utf-8"))
                rawadd = g.split("<div>")[1].split("</div>")[0]
                state = rawadd.rsplit(",", 1)[1].strip().split(" ")[0]
            if "'Phone Number','" in line:
                phone = line.split("'Phone Number','")[1].split("'")[0]
            if "'Visit Website','" in line:
                loc = line.split("'Visit Website','")[1].split("'")[0]
            if "','Get Directions','" in line:
                rawadd = line.split("','Get Directions','")[1].split("'")[0]
                add = rawadd.split(",")[0].strip()
                city = rawadd.split(",")[1].strip()
                zc = rawadd.split(",")[2].strip()
            if '<div class="kw-contact_button">' in line:
                info = name + "|" + add + "|" + city + "|" + phone
                if info not in ids:
                    ids.append(info)
                    if phone == "":
                        phone = "<MISSING>"
                    lat = "<MISSING>"
                    hours = "<MISSING>"
                    store = "<MISSING>"
                    lng = "<MISSING>"
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
