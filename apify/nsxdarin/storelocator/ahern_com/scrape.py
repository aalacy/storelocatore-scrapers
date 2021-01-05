import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("ahern_com")


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
    url = "https://www.ahern.com/skin/frontend/default/ahern/js/locations.js"
    r = session.get(url, headers=headers)
    website = "ahern.com"
    typ = "<MISSING>"
    country = "US"
    Found = False
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "plots: {" in line:
            Found = True
        if (
            Found
            and 'href: "/equipment-rental-' in line
            and "-nevada" not in line
            and "-fremont" not in line
            and "-oxnard" not in line
        ):
            locs.append("https://www.ahern.com" + line.split('"')[1])
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
        daycount = 0
        try:
            r2 = session.get(loc, headers=headers)
            for line2 in r2.iter_lines():
                line2 = str(line2.decode("utf-8"))
                if '<span itemprop="name">' in line2:
                    name = line2.split('<span itemprop="name">')[1].split("<")[0]
                if '<span itemprop="telephone">' in line2:
                    phone = line2.split('<span itemprop="telephone">')[1].split("<")[0]
                if 'itemprop="streetAddress">' in line2:
                    add = line2.split('itemprop="streetAddress">')[1].split("<")[0]
                    city = (
                        line2.split('<span itemprop="addressLocality">')[1]
                        .split("<")[0]
                        .strip()
                    )
                    try:
                        state = line2.split('<span itemprop="addressRegion">')[1].split(
                            "<"
                        )[0]
                        zc = line2.split('<span itemprop="postalCode">')[1].split("<")[
                            0
                        ]
                    except:
                        state = (
                            line2.split('<span itemprop="postalCode">')[1]
                            .split("<")[0]
                            .strip()
                        )
                        zc = (
                            line2.split('<span itemprop="postalCode">')[2]
                            .split("<")[0]
                            .strip()
                        )
                if '<iframe src="https://www.google.com/maps/' in line2:
                    lat = line2.split("!3d")[1].split("!")[0]
                    lng = line2.split("!2d")[1].split("!")[0]
                if '<link itemprop="dayOfWeek"' in line2:
                    day = (
                        line2.split('<link itemprop="dayOfWeek"')[1]
                        .split(">")[1]
                        .split("<")[0]
                    )
                if '<time itemprop="opens" content="' in line2:
                    day = day + ": " + line2.split('">')[1].split("<")[0].strip()
                if '<time itemprop="closes" content="' in line2:
                    day = day + "-" + line2.split('">')[1].split("<")[0].strip()
                    daycount = daycount + 1
                    if daycount <= 7:
                        if hours == "":
                            hours = day
                        else:
                            hours = hours + "; " + day
                if "Closed</time>" in line2:
                    daycount = daycount + 1
                    day = day + ": Closed"
                    if daycount <= 7:
                        if hours == "":
                            hours = day
                        else:
                            hours = hours + "; " + day
            if add != "":
                phone = phone.replace("Phone:", "").strip()
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
            pass


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
