import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("fostersfreeze_com")


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
    url = "https://fostersfreeze.com/locations/"
    r = session.get(url, headers=headers)
    website = "fostersfreeze.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<h6><a href="' in line:
            locs.append(
                "https://fostersfreeze.com/locations/"
                + line.split('<h6><a href="')[1].split('"')[0]
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
            if '<span itemprop="name">' in line2:
                name = line2.split('<span itemprop="name">')[1].split("<")[0]
            if 'streetAddress">' in line2:
                add = line2.split('streetAddress">')[1].split("<")[0]
            if '="addressLocality">' in line2:
                city = line2.split('="addressLocality">')[1].split("<")[0]
                state = line2.split('"addressRegion">')[1].split("<")[0]
                zc = (
                    line2.split('"addressRegion">')[1]
                    .split(">")[1]
                    .split("<")[0]
                    .strip()
                )
            if 'temprop="telephone">' in line2:
                phone = line2.split('op="telephone">')[1].split("<")[0]
            if lat == "" and "latitude:" in line2:
                lat = line2.split("latitude:")[1].split(",")[0]
            if lng == "" and "longitude:" in line2:
                lng = line2.split("longitude:")[1].split(",")[0]
            if "itemprop=openingHours><td>" in line2:
                days = line2.split("itemprop=openingHours><td>")
                for day in days:
                    if "<td class=opens>" in day:
                        hrs = (
                            day.split("<")[0]
                            + ": "
                            + day.split("<td class=opens>")[1].split("<")[0]
                            + "-"
                            + day.split("<td class=closes>")[1].split("<")[0]
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
