import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("drayerpt_com")


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
    url = "https://drayer.urpt.com/find-a-location/"
    r = session.get(url, headers=headers)
    website = "drayerpt.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'lat="' in line:
            llat = line.split('"')[1]
        if 'lng="' in line:
            llng = line.split('"')[1]
        if "Location Details</a>" in line:
            locs.append(
                "https://drayer.urpt.com"
                + line.split('href="')[1].split('"')[0]
                + "|"
                + llat
                + "|"
                + llng
            )
    for loc in locs:
        logger.info(loc)
        name = ""
        city = ""
        state = ""
        add = ""
        zc = ""
        phone = ""
        store = "<MISSING>"
        lat = loc.split("|")[1]
        lng = loc.split("|")[2]
        hours = ""
        r2 = session.get(loc.split("|")[0], headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if 'og:title" content="' in line2:
                name = line2.split('og:title" content="')[1].split('"')[0]
                if " - " in name:
                    name = name.split(" - ")[0]
                if " |" in name:
                    name = name.split(" |")[0]
            if '"col-lg-3">' in line2 and add == "":
                g = next(lines)
                g = str(g.decode("utf-8"))
                add = g.split(">")[1].split("<")[0]
                g = next(lines)
                g = str(g.decode("utf-8"))
                city = g.split(",")[0].strip().replace("\t", "")
                state = g.split(",")[1].strip().split(" ")[0]
                zc = g.split("<")[0].rsplit(" ", 1)[1]
                if "<" in zc:
                    zc = zc.split("<")[0]
            if '<a href="tel:+' in line2 and phone == "":
                phone = line2.split('<a href="tel:+')[1].split('"')[0]
            if '<span class="hours-content">' in line2:
                hrs = (
                    line2.split('<span class="hours-content">')[1].split("<")[0].strip()
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
                HFound = True
                while HFound:
                    g = next(lines)
                    g = str(g.decode("utf-8"))
                    if "</div>" in g:
                        HFound = False
                    else:
                        hrs = g.split("<")[0]
                        hours = hours + "; " + g
        hours = (
            hours.replace("&amp;", "&")
            .replace("<br />", "")
            .replace("</span>", "")
            .replace("</p>", "")
        )
        yield [
            website,
            loc.split("|")[0],
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
