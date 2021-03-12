import csv
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("whitecastle_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/json",
    "X-Requested-With": "XMLHttpRequest",
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
            ]
        )
        for row in data:
            writer.writerow(row)


def fetch_data():
    locs = []
    url = "https://www.whitecastle.com/sitemap.xml"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if "<loc>https://www.whitecastle.com/locations/" in line:
            locs.append(line.split("locations/")[1].split("<")[0])
    for loc in locs:
        logger.info(("Pulling Location %s..." % loc))
        lurl = (
            "https://www.whitecastle.com/wcapi/location-by-store-number?storeNumber="
            + loc
        )
        website = "whitecastle.com"
        name = "White Castle #" + loc
        store = loc
        hours = ""
        r2 = session.get(lurl, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        array = json.loads(r2.content)
        add = array["address"]
        city = array["city"]
        state = array["state"]
        zc = array["zip"]
        try:
            phone = array["telephone"]
        except:
            phone = "<MISSING>"
        country = "US"
        if array["open24x7"]:
            hours = "Open 24 Hours"
        else:
            try:
                for hr in array["days"]:
                    day = hr["day"]
                    if not hr["open24Hours"]:
                        time = hr["hours"]
                    else:
                        time = "Open 24 Hours"
                    if hours == "":
                        hours = day + ": " + time
                    else:
                        hours = hours + "; " + day + ": " + time
            except:
                hours = "Sun-Sat: Closed"
        typ = "Restaurant"
        try:
            lat = array["lat"]
        except:
            lat = "<MISSING>"
        try:
            lng = array["lng"]
        except:
            lng = "<MISSING>"
        yield [
            website,
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
