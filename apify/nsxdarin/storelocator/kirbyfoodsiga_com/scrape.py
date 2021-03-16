import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("kirbyfoodsiga_com")


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
    url = "https://www.kirbyfoodsiga.com/stores/search-stores.html"
    r = session.get(url, headers=headers)
    website = "kirbyfoodsiga.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<a href="/stores/store-search-results.html?state=' in line:
            states.append(
                "https://www.kirbyfoodsiga.com/stores/store-search-results.html?state="
                + line.split('<a href="/stores/store-search-results.html?state=')[
                    1
                ].split('"')[0]
            )
    for state in states:
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if ">See Store Details" in line2:
                locs.append(
                    "https://www.kirbyfoodsiga.com"
                    + line2.split('href="')[1].split('"')[0]
                )
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
            if 'itemprop="name">' in line2:
                name = line2.split('itemprop="name">')[1].split("<")[0]
            if '<span itemprop="streetAddress">' in line2:
                add = line2.split('<span itemprop="streetAddress">')[1].split("<")[0]
            if '<span itemprop="addressLocality">' in line2:
                city = line2.split('<span itemprop="addressLocality">')[1].split("<")[0]
                state = line2.split('<span itemprop="addressRegion">')[1].split("<")[0]
                zc = line2.split('"postalCode">')[1].split("<")[0]
            if '"phoneNumber" href="tel:' in line2:
                phone = (
                    line2.split('"phoneNumber" href="tel:')[1]
                    .split('"')[0]
                    .replace("+1", "")
                )
            if 'itemprop="openingHours" content="' in line2:
                hrs = line2.split('itemprop="openingHours" content="')[1].split('"')[0]
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if 'var storeLat = "' in line2:
                lat = line2.split('var storeLat = "')[1].split('"')[0]
            if 'ar storeLng = "' in line2:
                lng = (
                    line2.split('ar storeLng = "')[1]
                    .split('"')[0]
                    .replace("\\u002D", "-")
                )
        store = loc.split("store.")[1].split(".")[0]
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
