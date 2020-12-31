import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name="lifestorage.com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


session = SgRequests()


def fetch_data():
    # Your scraper here
    locs = []
    street = []
    states = []
    cities = []
    types = []
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    ids = []
    page_url = []
    countries = []

    res = session.get("https://www.lifestorage.com/")
    soup = BeautifulSoup(res.text, "html.parser")
    sls = soup.find("div", {"class": "footerStates"}).find_all("a")

    for sl in sls:
        url = "https://www.lifestorage.com" + sl.get("href")
        log.info(url)
        res = session.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        sa = soup.find_all("a", {"class": "btn store"})

        for a in sa:
            url = "https://www.lifestorage.com" + a.get("href")
            log.info(url)
            req = session.get(url)
            soup = BeautifulSoup(req.text, "lxml")
            data = "".join(
                soup.find_all("script", {"type": "application/ld+json"})[-1].contents
            )

            data = data.replace("[,", "[").replace("}{", "},{")

            js = json.loads(data)["@graph"][0]
            if (
                "coming soon" in js["image"]["name"].lower()
                or "opening soon" in js["image"]["name"].lower()
            ):
                continue
            page_url.append(url)
            locs.append(js["alternateName"])
            ids.append(js["branchCode"])
            addr = js["address"]
            street.append(addr["streetAddress"])
            states.append(addr["addressRegion"])
            cities.append(addr["addressLocality"])
            zips.append(addr["postalCode"])
            countries.append(addr["addressCountry"])
            timl = js["openingHoursSpecification"]
            tim = ""
            for l in timl:
                tim += l["dayOfWeek"] + ": " + l["opens"] + " - " + l["closes"] + " "
            if "Sunday:" not in tim:
                tim += "Sunday: Closed"
            timing.append(tim.strip())
            phones.append(js["telephone"])
            lat.append(js["geo"]["latitude"])
            long.append(js["geo"]["longitude"])
            types.append(js["@type"])

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.lifestorage.com/")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append(countries[i])
        row.append(ids[i])  # store #
        row.append(phones[i])  # phone
        row.append(types[i])  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append(timing[i])  # timing
        row.append(page_url[i])  # page url

        all.append(row)

    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
