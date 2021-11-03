import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("panerabread_com")


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
    locs = [
        "https://locations.panerabread.com/fl/odessa/16034-preserve-marketplace-blvd.html"
    ]
    states = []
    cities = []
    alllocs = []
    url = "https://locations.panerabread.com/index.html"
    r = session.get(url, headers=headers)
    website = "panerabread.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"c-directory-list-content-item-link" href="' in line:
            items = line.split('"c-directory-list-content-item-link" href="')
            for item in items:
                if 'count">(' in item and "Ontario" not in item:
                    count = item.split('count">(')[1].split(")")[0]
                    if count == "1":
                        locs.append(
                            "https://locations.panerabread.com/" + item.split('"')[0]
                        )
                    else:
                        if "dc/" in item:
                            cities.append(
                                "https://locations.panerabread.com/"
                                + item.split('"')[0]
                            )
                        else:
                            states.append(
                                "https://locations.panerabread.com/"
                                + item.split('"')[0]
                            )
    for state in states:
        logger.info(state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<a class="c-directory-list-content-item-link" href="' in line2:
                items = line2.split(
                    '<a class="c-directory-list-content-item-link" href="'
                )
                for item in items:
                    if 'count">(' in item:
                        count = item.split('count">(')[1].split(")")[0]
                        if count == "1":
                            locs.append(
                                "https://locations.panerabread.com/"
                                + item.split('"')[0]
                            )
                        else:
                            cities.append(
                                "https://locations.panerabread.com/"
                                + item.split('"')[0]
                            )
    for city in cities:
        logger.info(city)
        r2 = session.get(city, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '"c-location-grid-item-link" href="../' in line2:
                items = line2.split('"c-location-grid-item-link" href="..')
                for item in items:
                    if "View Location Details" in item:
                        locs.append(
                            "https://locations.panerabread.com/" + item.split('"')[0]
                        )
    for loc in locs:
        loc = loc.replace(".com//", ".com/").replace("&amp;", "&").replace("&#39;", "'")
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
                name = line2.split('<span class="location-name-geo">')[1].split("<")[0]
            if add == "" and '"c-address-street-1">' in line2:
                add = line2.split('"c-address-street-1">')[1].split("<")[0]
                try:
                    add = (
                        add
                        + " "
                        + line2.split('"c-address-street-2">')[1].split("<")[0]
                    )
                except:
                    pass
                add = add.strip()
                city = line2.split('itemprop="addressLocality">')[1].split("<")[0]
                state = line2.split('itemprop="addressRegion">')[1].split("<")[0]
                zc = line2.split('itemprop="postalCode">')[1].split("<")[0].strip()
                phone = (
                    line2.split('main-number-link" href="tel:')[1]
                    .split('"')[0]
                    .replace("+1", "")
                )
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[
                    0
                ]
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[
                    0
                ]
            if "data-days='[{" in line2 and hours == "":
                days = (
                    line2.split("data-days='[{")[1]
                    .split("]' data-showOpen")[0]
                    .split('"day":"')
                )
                for day in days:
                    if "isClosed" in day:
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
        if loc not in alllocs:
            alllocs.append(loc)
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
