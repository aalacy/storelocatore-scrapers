import csv
from sgrequests import SgRequests
import gzip
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("airgas_com")


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
    sitemaps = []
    url = "https://locations.airgas.com/sitemap/sitemap_index.xml"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>" in line:
            sitemaps.append(line.split(">")[1].split("<")[0])
    Total = True
    while Total:
        for sm in sitemaps:
            logger.info("Pulling Sitemap %s..." % sm)
            smurl = sm
            with open("branches.xml.gz", "wb") as f:
                r = session.get(smurl, headers=headers)
                f.write(r.content)
                f.close()
                with gzip.open("branches.xml.gz", "rb") as f:
                    for line in f:
                        line = str(line.decode("utf-8"))
                        if "<loc>https://locations.airgas.com" in line:
                            lurl = line.split("<loc>")[1].split("<")[0]
                            if ".html" in lurl:
                                if lurl not in locs:
                                    locs.append(lurl)
            logger.info(str(len(locs)) + " Locations Found...")
            if len(locs) >= 700:
                Total = False
    for loc in locs:
        website = "airgas.com"
        country = "US"
        hours = ""
        logger.info(loc)
        store = loc.rsplit(".", 1)[0].rsplit("-", 1)[1]
        typ = "<MISSING>"
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<h2 class="mt-20 mb-20">' in line2:
                name = line2.split('<h2 class="mt-20 mb-20">')[1].split("<")[0]
                if "|" in name:
                    typ = name.split("|")[0].strip()
            if '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if '<span class="daypart" data-daypart="' in line2:
                day = line2.split('<span class="daypart" data-daypart="')[1].split('"')[
                    0
                ]
            if '<span class="time-open">' in line2:
                hrs = line2.split('<span class="time-open">')[1].split("<")[0]
            if '"latitude": "' in line2:
                lat = line2.split('"latitude": "')[1].split('"')[0]
            if '"longitude": "' in line2:
                lng = line2.split('"longitude": "')[1].split('"')[0]
            if '<span class="time-close">' in line2:
                hrs = (
                    hrs
                    + "-"
                    + line2.split('<span class="time-close">')[1].split("<")[0]
                )
                hrinfo = day + ": " + hrs
                if hours == "":
                    hours = hrinfo
                else:
                    hours = hours + "; " + hrinfo
            if "<span>Closed</span>" in line2:
                hrs = "Closed"
                hrinfo = day + ": " + hrs
                if hours == "":
                    hours = hrinfo
                else:
                    hours = hours + "; " + hrinfo
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
