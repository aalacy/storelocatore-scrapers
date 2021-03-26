import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("pizzahut_com")

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
    url = "https://locations.pizzahut.com/"
    states = []
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if '<a class="Directory-listLink" href="' in line:
            items = line.split('<a class="Directory-listLink" href="')
            for item in items:
                if 'data-ya-track="todirectory"' in item:
                    state = item.split('"')[0]
                    states.append("https://locations.pizzahut.com/" + state)
    for state in states:
        cities = []
        locs = []
        logger.info(("Pulling State %s..." % state))
        r2 = session.get(state, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<a class="Directory-listLink" href="' in line2:
                items = line2.split('<a class="Directory-listLink" href="')
                for item in items:
                    if 'data-ya-track="todirectory"' in item:
                        city = item.split('"')[0]
                        curl = "https://locations.pizzahut.com/" + city
                        cities.append(curl)
        for city in cities:
            logger.info(("Pulling City %s..." % city))
            r2 = session.get(city, headers=headers)
            if r2.encoding is None:
                r2.encoding = "utf-8"
            for line2 in r2.iter_lines(decode_unicode=True):
                if '<a class="Teaser-titleLink" href="../' in line2:
                    items = line2.split('<a class="Teaser-titleLink" href="../')
                    for item in items:
                        if 'data-ya-track="businessname"' in item:
                            lurl = (
                                "https://locations.pizzahut.com/" + item.split('"')[0]
                            )
                            if lurl not in locs:
                                locs.append(lurl)
        for loc in locs:
            r3 = session.get(loc, headers=headers)
            if r3.encoding is None:
                r3.encoding = "utf-8"
            lines = r3.iter_lines(decode_unicode=True)
            country = "US"
            website = "pizzahut.com"
            typ = "Restaurant"
            hours = ""
            add = ""
            city = ""
            state = ""
            zc = ""
            lat = "<MISSING>"
            lng = "<MISSING>"
            store = ""
            phone = ""
            name = "Pizza Hut"
            for line3 in lines:
                if 'itemprop="streetAddress" content="' in line3:
                    add = line3.split('itemprop="streetAddress" content="')[1].split(
                        '"'
                    )[0]
                    city = line3.split('<span class="c-address-city">')[1].split("<")[0]
                    try:
                        state = line3.split(
                            'class="c-address-state" itemprop="addressRegion">'
                        )[1].split("<")[0]
                    except:
                        state = "<MISSING>"
                    try:
                        zc = line3.split('itemprop="postalCode">')[1].split("<")[0]
                    except:
                        zc = "<MISSING>"
                    try:
                        phone = line3.split('data-ya-track="phone">')[1].split("<")[0]
                    except:
                        phone = "<MISSING>"
                if 'itemprop="latitude" content="' in line3:
                    lat = line3.split('itemprop="latitude" content="')[1].split('"')[0]
                    lng = line3.split('<meta itemprop="longitude" content="')[1].split(
                        '"'
                    )[0]
                if '{"ids":' in line3:
                    store = line3.split('{"ids":')[1].split(",")[0]
                if "Carryout Hours</span>" in line3:
                    hrs = (
                        line3.split("Carryout Hours</span>")[1]
                        .split("data-days='")[1]
                        .split("]}]")[0]
                    )
                    days = hrs.split('"day":"')
                    try:
                        for day in days:
                            if '"intervals"' in day:
                                if hours == "":
                                    hours = (
                                        day.split('"')[0][:3]
                                        + ": "
                                        + day.split('"start":')[1].split("}")[0]
                                        + "-"
                                        + day.split('"end":')[1].split(",")[0]
                                    )
                                else:
                                    hours = (
                                        hours
                                        + "; "
                                        + day.split('"')[0][:3]
                                        + ": "
                                        + day.split('"start":')[1].split("}")[0]
                                        + "-"
                                        + day.split('"end":')[1].split(",")[0]
                                    )
                    except:
                        hours = "<MISSING>"
            if hours == "":
                hours = "<MISSING>"
            if add != "":
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
