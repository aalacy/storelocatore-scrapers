import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("kiehls_com")


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
    url = "https://stores.kiehls.com/index.html"
    r = session.get(url, headers=headers)
    website = "kiehls.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'list-content-item-link" href="' in line:
            items = line.split('list-content-item-link" href="')
            for item in items:
                if 'content-item-count">(' in item:
                    count = item.split('content-item-count">(')[1].split(")")[0]
                    if count == "1":
                        locs.append("https://stores.kiehls.com/" + item.split('"')[0])
                    else:
                        states.append("https://stores.kiehls.com/" + item.split('"')[0])
    for state in states:
        logger.info(state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'list-content-item-link" href="' in line2:
                items = line2.split('list-content-item-link" href="')
                for item in items:
                    if 'content-item-count">(' in item:
                        count = item.split('content-item-count">(')[1].split(")")[0]
                        if count == "1":
                            locs.append(
                                "https://stores.kiehls.com/" + item.split('"')[0]
                            )
                        else:
                            cities.append(
                                "https://stores.kiehls.com/" + item.split('"')[0]
                            )
    for city in cities:
        logger.info(city)
        r2 = session.get(city, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<a class="c-location-grid-item-link" href="../' in line2:
                items = line2.split('<a class="c-location-grid-item-link" href="../')
                for item in items:
                    if "Store Details" in item:
                        locs.append("https://stores.kiehls.com/" + item.split('"')[0])
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
            if '<span class="location-name-geo">' in line2:
                name = (
                    "Kiehl's "
                    + line2.split('<span class="location-name-geo">')[1]
                    .split("<")[0]
                    .title()
                )
                add = line2.split('<span class="c-address-street-1">')[1].split("<")[0]
                city = line2.split('"addressLocality">')[1].split("<")[0]
                state = line2.split('"addressRegion">')[1].split("<")[0]
                zc = line2.split('itemprop="postalCode">')[1].split("<")[0].strip()
                phone = line2.split('main-number-link" href="tel:+')[1].split('"')[0]
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[
                    0
                ]
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[
                    0
                ]
                days = line2.split("data-days='[")[1].split("}]'")[0].split('"day":"')
                for day in days:
                    if '"start":' in day:
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
