import csv
import requests  # ignore_check
from requests.exceptions import ConnectionError
from sgrequests import SgRequests
import collections
from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name="redroof.com")


def override_retries():
    # monkey patch sgrequests in order to set max retries
    def new_init(self):
        requests.packages.urllib3.disable_warnings()
        self.session = self.requests_retry_session(retries=0)

    SgRequests.__init__ = new_init


override_retries()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
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
            if row:
                writer.writerow(row)


def get_sitemap(attempts=1):
    if attempts > 10:
        log.error("Couldn't get sitemap after 10 attempts")
        raise SystemExit
    try:
        session = SgRequests()
        url = "https://www.redroof.com/sitemap.xml"
        r = session.get(url, headers=headers)
        return r
    except (ConnectionError, Exception) as ex:
        log.error(f"Exception getting sitemap: {str(ex)}")
        return get_sitemap(attempts=attempts + 1)


def fetch_data():
    locs = []
    r = get_sitemap()
    for line in r.iter_lines(decode_unicode=True):
        if "property/" in line:
            lurl = "https://www.redroof.com/" + line.split("<loc>")[1].split("<")[0]
            locs.append(lurl)

    q = collections.deque(locs)
    attempts = {}
    while q:
        loc = q.popleft()
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        phone = ""
        website = "redroof.com"
        typ = ""
        lat = ""
        lng = ""
        hours = "<MISSING>"
        store = loc.rsplit("/", 1)[1]
        r2 = None
        try:
            session = SgRequests()
            page_url = (
                f"https://www.redroof.com/api/GetPropertyDetail?PropertyId={store}"
            )
            r2 = session.get(page_url, headers=headers)
        except (ConnectionError, Exception) as ex:
            log.info("Failed to connect to " + loc)
            log.info(f"Exception: {str(ex)}")
            if attempts.get(loc, 0) >= 3:
                log.error("giving up on " + loc)
            else:
                q.append(loc)
                attempts[loc] = attempts.get(loc, 0) + 1
                log.info("attempts: " + str(attempts[loc]))
            continue

        data = r2.json().get("SDLKeyValuePairs").get("ServicePropertyDetails")

        name = data["Description"]
        add = data["Street1"] + (", " + data["Street2"] if data["Street2"] else "")
        city = data["City"]
        state = data["State"]
        zc = data["PostalCode"]
        phone = data["PhoneNumber"]
        typ = data["PropertyType"]
        lat = data["Latitude"]
        lng = data["Longitude"]
        country = data["Country"]

        if country != "US" and country != "CA":
            yield None
            continue

        location = [
            website,
            page_url,
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
        location = [str(x) if x else "<MISSING>" for x in location]

        yield location


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
