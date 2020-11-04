import csv
from sgrequests import SgRequests
import requests_random_user_agent  # ignore_check
import collections
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('7-eleven_com')

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,la;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1"
    # the `requests_random_user_agent` package automatically rotates user-agent strings
    # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
}


def override_retries():
    # monkey patch sgrequests in order to set max retries ...
    # we will control retries in this script in order to reset the session and get a new IP each time
    import requests  # ignore_check

    def new_init(self):
        requests.packages.urllib3.disable_warnings()
        self.session = self.requests_retry_session(retries=0)

    SgRequests.__init__ = new_init


override_retries()
session = SgRequests()
show_logs = False


def log(*args, **kwargs):
    if show_logs == True:
        logger.info(" ".join(map(str, args)), **kwargs)
        logger.info("")


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


def get(url, headers, attempts=0):
    global session

    max_attempts = 10
    if attempts > max_attempts:
        logger.info(f"Exceeded max attempts ({max_attempts}) for URL: {url}")

    try:
        r = session.get(url, headers=headers)
        log(f"Status {r.status_code} for URL: {url}")
        r.raise_for_status()
        return r
    except Exception as ex:
        log(f"---  Resetting session after exception --> {ex} ")
        session = SgRequests()
        return get(url, headers, attempts + 1)


def fetch_data():
    states = []
    url = "https://www.7-eleven.com/locations"
    r = get(url, headers=headers)
    for line in r.iter_lines(decode_unicode=True):
        if '<li><a href="/locations/' in line:
            items = line.split('<li><a href="/locations/')
            for item in items:
                if "All Stores" not in item:
                    states.append(
                        "https://www.7-eleven.com/locations/" + item.split('"')[0]
                    )

    log(*states, sep="\n")

    for state in states:
        cities = []
        locs = []
        log("Pulling State %s..." % state)
        r2 = get(state, headers=headers)
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<li><a href="/locations/' in line:
                items = line2.split('<li><a href="/locations/')
                for item in items:
                    if 'class="locations-list">' not in item:
                        if "wv" in state and "st-albans" in item:
                            pass
                        else:
                            cities.append(
                                "https://www.7-eleven.com/locations/"
                                + item.split('"')[0]
                            )
        for city in cities:
            r3 = get(city, headers=headers)
            for line3 in r3.iter_lines(decode_unicode=True):
                if 'class="se-amenities se-local-store" href="/locations/' in line3:
                    items = line3.split(
                        'class="se-amenities se-local-store" href="/locations/'
                    )
                    for item in items:
                        if "<!DOCTYPE html>" not in item and "st-albans" not in item:
                            locs.append(
                                "https://www.7-eleven.com/locations/"
                                + item.split('"')[0]
                            )

        q = collections.deque(locs)

        while q:
            loc = q.popleft()
            website = "7-eleven.com"
            typ = ""
            name = "7-Eleven"
            hours = ""
            phone = ""
            store = ""
            city = ""
            add = ""
            state = ""
            zc = ""
            lat = ""
            lng = ""
            country = "US"

            r2 = get(loc, headers=headers)
            for line2 in r2.iter_lines(decode_unicode=True):
                if '"hours":{"message":"' in line2:
                    hours = line2.split('"hours":{"message":"')[1].split('"')[0]
                if '"localStoreLatLon":{"lat":' in line2:
                    lat = line2.split('"localStoreLatLon":{"lat":')[1].split(",")[0]
                    lng = line2.split(',"lon":')[1].split("}")[0]
                if '"currentStoreID":' in line2:
                    store = line2.split('"currentStoreID":')[1].split(",")[0]
                if '<div class="background-gradient"></div><h5>' in line2:
                    typ = line2.split('<div class="background-gradient"></div><h5>')[
                        1
                    ].split("<")[0]
                if '"localStoreData":{"currentStore":' in line2:
                    phone = (
                        line2.split('"localStoreData":{"currentStore":')[1]
                        .split('"phone":"')[1]
                        .split('"')[0]
                    )
                    add = (
                        line2.split('"localStoreData":{"currentStore":')[1]
                        .split('"address":"')[1]
                        .split('"')[0]
                    )
                    zc = (
                        line2.split('"localStoreData":{"currentStore":')[1]
                        .split('"zip":"')[1]
                        .split('"')[0]
                    )
                    state = (
                        line2.split('"localStoreData":{"currentStore":')[1]
                        .split('"state":"')[1]
                        .split('"')[0]
                    )
                    city = (
                        line2.split('"localStoreData":{"currentStore":')[1]
                        .split('"city":"')[1]
                        .split('"')[0]
                    )
            if hours == "":
                hours = "<MISSING>"
            if phone == "":
                phone = "<MISSING>"
            if "00000000" not in phone and add != "":
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
