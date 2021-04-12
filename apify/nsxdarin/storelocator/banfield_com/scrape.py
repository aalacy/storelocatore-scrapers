import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("banfield_com")


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
    url = "https://www.banfield.com/sitemap.xml"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if "<loc>https://www.banfield.com/locations/veterinarians/" in line:
            lurl = line.split("<loc>")[1].split("<")[0]
            if lurl.count("/") == 7:
                locs.append(lurl)
    for loc in locs:
        logger.info(("Pulling Location %s..." % loc))
        website = "banfield.com"
        typ = "Hospital"
        hours = ""
        name = ""
        add = ""
        city = ""
        state = ""
        country = "US"
        lat = ""
        lng = ""
        phone = ""
        store = ""
        zc = ""
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        for line2 in r2.iter_lines(decode_unicode=True):
            if 'alt="PetSmart-logo"' in line2:
                typ = "Petsmart"
            if '"addressLocality":"' in line2:
                city = line2.split('"addressLocality":"')[1].split('"')[0]
            if '"addressRegion":"' in line2:
                state = line2.split('"addressRegion":"')[1].split('"')[0]
            if '"postalCode":"' in line2:
                zc = line2.split('"postalCode":"')[1].split('"')[0]
            if '"streetAddress":"' in line2:
                add = line2.split('"streetAddress":"')[1].split('"')[0].strip()
            if '"telephone":"' in line2:
                phone = line2.split('"telephone":"')[1].split('"')[0]
            if '"latitude":"' in line2:
                lat = line2.split('"latitude":"')[1].split('"')[0]
            if '"longitude":"' in line2:
                lng = line2.split('"longitude":"')[1].split('"')[0]
            if '"name":"' in line2:
                name = line2.split('"name":"')[1].split('"')[0]
            if '"dayOfWeek":"' in line2:
                day = line2.split('"dayOfWeek":"')[1].split('"')[0]
            if '"opens":"' in line2:
                op = line2.split('"opens":"')[1].split('"')[0]
            if '"closes":"' in line2:
                cl = line2.split('"closes":"')[1].split('"')[0]
                hrs = day + ": " + op + "-" + cl
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if '<link rel="canonical" href="' in line2:
                store = (
                    line2.split('<link rel="canonical" href="')[1]
                    .split('"')[0]
                    .rsplit("/", 1)[1]
                )
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
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


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
