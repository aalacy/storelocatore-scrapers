import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("libertytax_com")

session = SgRequests()
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
            writer.writerow(row)


def fetch_data():
    states = []
    url = "https://www.libertytax.com/income-tax-preparation-locations.html"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if '"State":"' in line:
            items = line.split('"State":"')
            for item in items:
                if '"StateUrl":"' in item:
                    states.append(
                        "https://www.libertytax.com"
                        + item.split('"StateUrl":"')[1].split('"')[0]
                    )
    for state in states:
        locs = []
        logger.info(("Pulling State %s..." % state))
        r2 = session.get(state, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        for line2 in r2.iter_lines(decode_unicode=True):
            if 'target="_blank" href="/income' in line2:
                items = line2.split('target="_blank" href="/income')
                for item in items:
                    if "margin-top" in item:
                        locs.append(
                            "https://www.libertytax.com/income" + item.split('"')[0]
                        )
        for loc in locs:
            logger.info(loc)
            LFound = True
            while LFound:
                try:
                    LFound = False
                    website = "libertytax.com"
                    typ = "<MISSING>"
                    hours = ""
                    name = ""
                    add = ""
                    city = ""
                    state = ""
                    zc = ""
                    country = "US"
                    store = loc.rsplit("/", 1)[1].split(".")[0]
                    phone = ""
                    lat = ""
                    lng = ""
                    r2 = session.get(loc, headers=headers)
                    if r2.encoding is None:
                        r2.encoding = "utf-8"
                    hcount = 0
                    for line2 in r2.iter_lines(decode_unicode=True):
                        if '<section class="office-details-body-text">' in line2:
                            hcount = hcount + 1
                        if "<h1>" in line2:
                            name = line2.split("<h1>")[1].split("<")[0]
                        if '"streetAddress": "' in line2:
                            add = line2.split('"streetAddress": "')[1].split('"')[0]
                        if '"addressLocality": "' in line2:
                            city = line2.split('"addressLocality": "')[1].split('"')[0]
                        if '"addressRegion": "' in line2:
                            state = line2.split('"addressRegion": "')[1].split('"')[0]
                        if '"postalCode": "' in line2:
                            zc = line2.split('"postalCode": "')[1].split('"')[0]
                        if '"telephone": "' in line2:
                            phone = line2.split('"telephone": "')[1].split('"')[0]
                        if "Latitude:" in line2:
                            lat = line2.split("Latitude:")[1].split(",")[0].strip()
                        if "Longitude:" in line2:
                            lng = line2.split("Longitude:")[1].split(",")[0].strip()
                        if '<span class="office-day-name">' in line2 and hcount == 0:
                            day = line2.split('<span class="office-day-name">')[
                                1
                            ].split("<")[0]
                        if '<span class="office-day-hours">' in line2 and hcount == 0:
                            hrs = line2.split('<span class="office-day-hours">')[
                                1
                            ].split("<")[0]
                            if hours == "":
                                hours = day + ": " + hrs
                            else:
                                hours = hours + "; " + day + ": " + hrs
                    if hours == "":
                        hours = "<MISSING>"
                    if phone == "":
                        phone = "<MISSING>"
                    if "00000" in lat or "00000" in lng:
                        lat = "<MISSING>"
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
                except:
                    LFound = True


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
