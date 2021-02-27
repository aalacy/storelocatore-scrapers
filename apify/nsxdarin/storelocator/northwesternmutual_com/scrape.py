import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("northwesternmutual_com")

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
    url = "https://www.northwesternmutual.com/office/"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if '<a href="' in line:
            locs.append(
                "https://www.northwesternmutual.com/office/"
                + line.split('href="')[1].split('"')[0]
            )
    for loc in locs:
        logger.info("Pulling Location %s..." % loc)
        website = "northwesternmutual.com"
        typ = "Financial Advisor"
        hours = "<MISSING>"
        add = ""
        city = ""
        phone = ""
        state = ""
        country = "US"
        zc = ""
        lat = ""
        lng = ""
        store = "<MISSING>"
        PFound = True
        while PFound:
            try:
                PFound = False
                r2 = session.get(loc, headers=headers)
                if r2.encoding is None:
                    r2.encoding = "utf-8"
                for line2 in r2.iter_lines(decode_unicode=True):
                    if '<p class="nmxo-utility-nav--text">' in line2:
                        name = (
                            line2.split('<p class="nmxo-utility-nav--text">')[1]
                            .split("<")[0]
                            .strip()
                        )
                    if '"streetAddress": "' in line2:
                        add = line2.split('"streetAddress": "')[1].split('"')[0]
                    if '"addressLocality": "' in line2:
                        city = line2.split('"addressLocality": "')[1].split('"')[0]
                    if '"addressRegion": "' in line2:
                        state = line2.split('"addressRegion": "')[1].split('"')[0]
                    if '"postalCode": "' in line2:
                        zc = line2.split('"postalCode": "')[1].split('"')[0]
                    if '"telePhone": "' in line2:
                        phone = line2.split('"telePhone": "')[1].split('"')[0]
                    if '"openingHours": "' in line2:
                        hours = line2.split('"openingHours": "')[1].split('"')[0]
                    if '"latitude": "' in line2:
                        lat = line2.split('"latitude": "')[1].split('"')[0]
                    if '"longitude": "' in line2:
                        lng = line2.split('"longitude": "')[1].split('"')[0]
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
                PFound = True


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
