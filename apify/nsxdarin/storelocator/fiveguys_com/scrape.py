import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("fiveguys_com")


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
    url = "https://restaurants.fiveguys.com/sitemap.xml"
    r = session.get(url, headers=headers)
    website = "fiveguys.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    Found = True
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "https://restaurants.fiveguys.com/al" in line:
            Found = False
        if "<loc>https://restaurants.fiveguys.com/" in line and Found:
            locs.append(line.split("<loc>")[1].split("<")[0].replace("&#39;", "'"))
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if name == "" and '<span class="LocationName-geo">' in line2:
                name = line2.split('<span class="LocationName-geo">')[1].split("<")[0]
            if 'itemprop="streetAddress" content="' in line2:
                add = line2.split('itemprop="streetAddress" content="')[1].split('"')[0]
                state = line2.split('itemprop="addressRegion">')[1].split("<")[0]
                city = line2.split('temprop="addressLocality" content="')[1].split('"')[
                    0
                ]
                zc = line2.split('itemprop="postalCode">')[1].split("<")[0]
            if 'id="phone-main">' in line2:
                phone = line2.split('id="phone-main">')[1].split("<")[0]
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[
                    0
                ]
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[
                    0
                ]
            if hours == "" and '<div class="Hero-hoursToday"><span class=' in line2:
                days = (
                    line2.split('<div class="Hero-hoursToday"><span class=')[1]
                    .split("data-days='[")[1]
                    .split("data-utc-offsets=")[0]
                    .split('"day":"')
                )
                for day in days:
                    if '"intervals":' in day:
                        if ',"isClosed":true' in day:
                            hrs = day.split('"')[0] + ": Closed"
                        else:
                            hrs = (
                                day.split('"')[0]
                                + ": "
                                + day.split('"start":')[1].split("}")[0]
                                + "-"
                                + day.split('"end":')[1].split(",")[0]
                            )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
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
