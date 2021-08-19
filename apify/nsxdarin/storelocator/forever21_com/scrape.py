import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("forever21_com")


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
    url = "https://locations.forever21.com/us/directory"
    r = session.get(url, headers=headers)
    website = "capriottis.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'href="../us/' in line:
            items = line.split('href="../us/')
            for item in items:
                if 'data-count="(' in item:
                    count = item.split('data-count="(')[1].split(")")[0]
                    lurl = "https://locations.forever21.com/us/" + item.split('"')[0]
                    if count == "1":
                        locs.append(lurl)
                    else:
                        states.append(lurl)
    for state in states:
        r2 = session.get(state, headers=headers)
        logger.info(state)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '"Directory-listLink" href="' in line2:
                items = line2.split('"Directory-listLink" href="')
                for item in items:
                    if 'data-count="(' in item:
                        count = item.split('data-count="(')[1].split(")")[0]
                        if count == "1":
                            lurl = (
                                "https://locations.forever21.com/"
                                + item.split("../../../")[1].split('"')[0]
                            )
                            locs.append(lurl)
                        else:
                            lurl = (
                                "https://locations.forever21.com/"
                                + item.split("../../../")[1].split('"')[0]
                            )
                            cities.append(lurl)
    for city in cities:
        r2 = session.get(city, headers=headers)
        logger.info(city)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'href="../../../../us/stores/' in line2:
                items = line2.split('href="../../../../us/stores/')
                for item in items:
                    if ">View Store<" in item:
                        lurl = (
                            "https://locations.forever21.com/us/stores/"
                            + item.split('"')[0]
                        )
                        locs.append(lurl)
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = loc.split("us/stores/")[1].split("/")[0].upper()
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<h1 class="Hero-title" itemprop="name">' in line2:
                name = line2.split('<h1 class="Hero-title" itemprop="name">')[1].split(
                    "<"
                )[0]
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[
                    0
                ]
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[
                    0
                ]
            if 'itemprop="streetAddress" content="' in line2:
                add = line2.split('itemprop="streetAddress" content="')[1].split('"')[0]
            if city == "" and 'Address-field Address-city">' in line2:
                city = line2.split('Address-field Address-city">')[1].split("<")[0]
            if 'itemprop="postalCode">' in line2:
                zc = line2.split('itemprop="postalCode">')[1].split("<")[0]
            if 'itemprop="telephone">' in line2:
                phone = line2.split('itemprop="telephone">')[1].split("<")[0]
            if hours == "" and 'today" data-days=' in line2:
                days = (
                    line2.split('today" data-days=')[1]
                    .split("]' data-utc")[0]
                    .split('"day":"')
                )
                for day in days:
                    if "intervals" in day:
                        if '"isClosed":false' not in day:
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
