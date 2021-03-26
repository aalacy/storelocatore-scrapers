import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("macys_com")

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
                "operating_info",
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
    url = "https://l.macys.com/sitemap.xml"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if "<loc>https://l.macys.com/" in line and ".html" not in line:
            lurl = line.split("<loc>")[1].split("<")[0]
            if lurl.count("/") == 3:
                locs.append(lurl)
    for loc in locs:
        logger.info(("Pulling Location %s..." % loc))
        website = "macys.com"
        typ = "<MISSING>"
        hours = ""
        name = ""
        opinfo = "<MISSING>"
        country = "US"
        city = ""
        add = ""
        zc = ""
        state = ""
        lat = ""
        lng = ""
        phone = ""
        store = ""
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        for line2 in r2.iter_lines(decode_unicode=True):
            if (
                'Thursday</td><td class="c-hours-details-row-intervals">Closed</td>'
                in line2
            ):
                opinfo = "Closed"
            if name == "" and '<span class="LocationName-geo">' in line2:
                name = (
                    "Macy's "
                    + line2.split('<span class="LocationName-geo">')[1].split("<")[0]
                )
            if '"address":' in line2:
                add = line2.split('"line1":"')[1].split('"')[0]
                try:
                    add = add + " " + line2.split('"line2":"')[1].split('"')[0]
                except:
                    pass
                city = line2.split('"city":"')[1].split('"')[0]
                state = line2.split('"region":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
            if phone == "" and '<meta itemprop="telephone" content="' in line2:
                phone = (
                    line2.split('<meta itemprop="telephone" content="')[1]
                    .split('"')[0]
                    .replace("+", "")
                )
            if 'itemprop="openingHours" content="' in line2:
                days = line2.split('itemprop="openingHours" content="')
                for day in days:
                    if "<!doctype html>" not in day:
                        hrs = day.split('"')[0]
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
            if 'entityType":"location","id":"' in line2:
                store = line2.split('entityType":"location","id":"')[1].split('"')[0]
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[
                    0
                ]
            if '<meta itemprop="longitude" content="' in line2:
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[
                    0
                ]
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        yield [
            website,
            loc,
            name,
            opinfo,
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
