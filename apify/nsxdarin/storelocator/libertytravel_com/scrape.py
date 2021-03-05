import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("libertytravel_com")


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
    locs = []
    url = "https://www.libertytravel.com/sitemap.xml"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if "/stores/" in line:
            locs.append(line.split(">")[1].split("<")[0])
    for loc in locs:
        logger.info(("Pulling Location %s..." % loc))
        rs = session.get(loc, headers=headers)
        website = "libertytravel.com"
        name = "<MISSING>"
        add = "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        zc = "<MISSING>"
        phone = "<MISSING>"
        hours = ""
        country = "US"
        typ = "<MISSING>"
        store = "<MISSING>"
        lat = "<MISSING>"
        lng = "<MISSING>"
        for line2 in rs.iter_lines(decode_unicode=True):
            if 'name="geo.placename" content="' in line2:
                name = line2.split('name="geo.placename" content="')[1].split('"')[0]
            if 'name="geo.position" content="' in line2:
                lat = line2.split('name="geo.position" content="')[1].split(",")[0]
                lng = (
                    line2.split('name="geo.position" content="')[1]
                    .split(",")[1]
                    .split('"')[0]
                    .strip()
                )
            if 'property="og:street_address" content="' in line2:
                add = line2.split('property="og:street_address" content="')[1].split(
                    '"'
                )[0]
            if 'property="og:locality" content="' in line2:
                city = line2.split('property="og:locality" content="')[1].split('"')[0]
            if 'property="og:region" content="' in line2:
                state = line2.split('property="og:region" content="')[1].split('"')[0]
            if 'property="og:postal_code" content="' in line2:
                zc = line2.split('property="og:postal_code" content="')[1].split('"')[0]
            if 'property="og:phone_number" content="' in line2:
                phone = line2.split('property="og:phone_number" content="')[1].split(
                    '"'
                )[0]
            if '<div class="store-open-days">' in line2:
                hrs = (
                    line2.split('<div class="store-open-days">')[1].split("<")[0] + ": "
                )
            if '<div class="store-open-hours">' in line2:
                hrs = (
                    hrs + line2.split('<div class="store-open-hours">')[1].split("<")[0]
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        if hours == "":
            hours = "<MISSING>"
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
