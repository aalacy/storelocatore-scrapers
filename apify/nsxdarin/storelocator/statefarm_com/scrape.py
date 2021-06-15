import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("statefarm_com")

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
    locs = []
    states = []
    cities = []
    url = "https://www.statefarm.com/agent/us"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if 'href="/agent/us/' in line:
            states.append(
                "https://www.statefarm.com" + line.split('href="')[1].split('"')[0]
            )
    for state in states:
        r2 = session.get(state, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        logger.info(("Pulling State %s..." % state))
        for line2 in r2.iter_lines(decode_unicode=True):
            if 'href="/agent/us/' in line2:
                cities.append(
                    "https://www.statefarm.com" + line2.split('href="')[1].split('"')[0]
                )
    for city in cities:
        r2 = session.get(city, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        logger.info("Pulling City %s..." % city)
        country = "US"
        typ = "<MISSING>"
        website = "statefarm.com"
        hours = ""
        lat = "<MISSING>"
        lng = "<MISSING>"
        loc = "<MISSING>"
        lines = r2.iter_lines(decode_unicode=True)
        for line2 in lines:
            if 'alt="Insurance Agent' in line2:
                phone = ""
                store = ""
                loc = ""
                hours = ""
                name = line2.split('alt="Insurance Agent')[1].split('"')[0].strip()
            if "map?office" in line2:
                g = next(lines)
                h = next(lines)
                i = next(lines)
                add = g.split('">')[1].split("<")[0].strip()
                if "&nbsp;" in h:
                    csz = (
                        h.strip().replace("\t", "").replace("\n", "").replace("\r", "")
                    )
                else:
                    add = add + " " + h.split("<")[0].strip()
                    csz = (
                        i.strip().replace("\t", "").replace("\n", "").replace("\r", "")
                    )
                city = csz.split(",")[0]
                state = csz.split("&nbsp;")[1]
                zc = csz.rsplit(";", 1)[1]
            if 'href="tel:' in line2:
                phone = line2.split('href="tel:')[1].split('"')[0]
            if '<a href="https://www.statefarm.com/agent/us/' in line2:
                loc = line2.split('href="')[1].split('"')[0]
                r3 = session.get(loc, headers=headers)
                HFound = False
                for line3 in r3.iter_lines():
                    line3 = str(line3.decode("utf-8"))
                    if '">Office Hours' in line3:
                        HFound = True
                    if HFound and '<div class="' in line3:
                        HFound = False
                    if 'data-latitude="' in line3:
                        lat = line3.split('data-latitude="')[1].split('"')[0]
                    if 'data-longitude="' in line3:
                        lng = line3.split('data-longitude="')[1].split('"')[0]
                    if '-oneX-body--primary">' in line3 and HFound:
                        hrs = line3.split('-oneX-body--primary">')[1].split("<")[0]
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
            if "Email agent</a>" in line2:
                store = line2.split('id="')[1].split('"')[0]
                if phone == "":
                    phone = "<MISSING>"
                if hours == "":
                    hours = "<MISSING>"
                if loc not in locs:
                    locs.append(loc)
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
