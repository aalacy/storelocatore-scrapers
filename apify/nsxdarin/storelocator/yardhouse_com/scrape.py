import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("yardhouse_com")


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
    session = SgRequests()
    url = "https://www.yardhouse.com/locations/all-locations?orderOnline=true"
    r = session.get(url, headers=headers)
    website = "yardhouse.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<a id="locDetailsId" href="' in line:
            locs.append(
                "https://www.yardhouse.com"
                + line.split('<a id="locDetailsId" href="')[1].split('"')[0]
            )
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = ""
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        session = SgRequests()
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '"streetAddress":"' in line2:
                name = line2.split('"name":"')[1].split('"')[0]
                try:
                    hours = (
                        line2.split('"openingHours":["')[1]
                        .split('"]')[0]
                        .replace('","', "; ")
                    )
                except:
                    hours = "<MISSING>"
                add = line2.split('"streetAddress":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                city = line2.split('"addressLocality":"')[1].split('"')[0]
                state = line2.split('"addressRegion":"')[1].split('"')[0]
                lat = line2.split('"latitude":"')[1].split('"')[0]
                lng = line2.split('"longitude":"')[1].split('"')[0]
                store = line2.split('"branchCode":"')[1].split('"')[0]
                phone = line2.split('"telephone":"')[1].split('"')[0]
        if "kansas-city-downtown-pl-district" in loc:
            add = "1300 Main Street"
            city = "Kansas City"
            state = "MO"
            zc = "64105"
            phone = "(816) 527-0952"
            hours = "Sun-Sat: 11:00AM - 10:00PM"
            store = "8359"
            name = "KANSAS CITY - DOWNTOWN P&L DISTRICT"
        if "san-antonio-the-shops-at-la-cantera" in loc:
            name = "SAN ANTONIO - THE SHOPS AT LA CANTERA"
            add = "15900 La Cantera Parkway  Bldg 23"
            city = "San Antonio"
            state = "TX"
            zc = "78256"
            phone = "(210) 691-0033"
        if zc == "":
            zc = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if state == "":
            state = "<MISSING>"
        if hours == "":
            hours = "<MISSING>"
        if lat == "":
            lat = "<MISSING>"
            lng = "<MISSING>"
        if city == "":
            city = "<MISSING>"
        if store == "":
            store = "<MISSING>"
        if add == "":
            add = "<MISSING>"
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
