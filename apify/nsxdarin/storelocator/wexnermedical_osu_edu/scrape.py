import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("wexnermedical_osu_edu")


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
    url = (
        "https://wexnermedical.osu.edu/locations/locations_filter/?name=&service=&care="
    )
    r = session.get(url, headers=headers)
    website = "wexnermedical.osu.edu"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    logger.info("Pulling Stores")
    name = "Central Ohio Primary Care"
    lat = "<MISSING>"
    lng = "<MISSING>"
    add = "4895 Olentangy Rd. Suite 150"
    city = "Columbus"
    state = ("OH",)
    zc = "43214"
    store = "<MISSING>"
    hours = "<MISSING>"
    phone = "<MISSING>"
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
    name = "Ohio State Transplant Care at the Jewish Hospital - Mercy Health"
    lat = "<MISSING>"
    lng = "<MISSING>"
    loc = "<MISSING>"
    add = "4700 E. Galbraith Rd., Suite 104"
    city = "Cincinnati"
    state = ("OH",)
    zc = "45236"
    store = "<MISSING>"
    hours = "<MISSING>"
    phone = "<MISSING>"
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
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"Url":"' in line:
            items = line.split('"Url":"')
            for item in items:
                if '"ServiceName":"' in item:
                    locs.append(item.split('"')[0])
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
            if '<meta property="og:title" content="' in line2:
                name = line2.split('<meta property="og:title" content="')[1].split('"')[
                    0
                ]
            if '<h1 class="globalpagetitle">' in line2:
                name = line2.split('<h1 class="globalpagetitle">')[1].split("<")[0]
            if '"latitude": "' in line2:
                lat = line2.split('"latitude": "')[1].split('"')[0]
            if '"longitude": "' in line2:
                lng = line2.split('"longitude": "')[1].split('"')[0]
            if '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if '"postalCode" : "' in line2:
                zc = line2.split('"postalCode" : "')[1].split('"')[0]
            if '"openingHours": [' in line2:
                hours = (
                    line2.split('"openingHours": [')[1]
                    .split("]")[0]
                    .replace('","', "; ")
                    .replace('"', "")
                )
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if '"openingHours": "' in line2:
                hours = line2.split('"openingHours": "')[1].split('"')[0]
            if '<span class="phoneLink">' in line2:
                phone = line2.split('<span class="phoneLink">')[1].split("<")[0]
        if "Ohio" in name:
            state = "Ohio"
        if "Mary Rutan" in add:
            add = "Mary Rutan Hospital Orthopedics 2221 Timber Trail"
        if phone == "":
            phone = "<MISSING>"
        if hours == "":
            hours = "<MISSING>"
        if lat == "":
            lat = "<MISSING>"
            lng = "<MISSING>"
        if add != "":
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
