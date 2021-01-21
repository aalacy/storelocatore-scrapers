import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("unitedcheckcashing_com")


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
    url = "http://www.unitedcheckcashing.com/locations"
    r = session.get(url, headers=headers)
    website = "unitedcheckcashing.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'class="detail_location" ><a href="store/' in line:
            locs.append(
                "https://www.unitedcheckcashing.com/"
                + line.split('href="')[1].split('"')[0]
            )
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = loc.rsplit("/", 1)[1]
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "<h2>" in line2:
                name = line2.split(">")[1].split("<")[0]
            if 'location_center_left">' in line2:
                next(lines)
                g = next(lines)
                g = str(g.decode("utf-8"))
                add = g.split(">")[1].split("<")[0]
                g = next(lines)
                g = str(g.decode("utf-8"))
                g = g.split(">")[1].split("<")[0].strip()
                city = g.split(",")[0]
                state = g.split(",")[1].strip().split(" ")[0]
                zc = g.rsplit(" ", 1)[1]
            if "Phone" in line2 and 'phone-call inlinelnk" href="tel:' in line2:
                phone = line2.split('phone-call inlinelnk" href="tel:')[1].split('"')[0]
            if 'onclick="loadmap("' in line2:
                lat = line2.split('onclick="loadmap("')[1].split('"')[0]
                lng = line2.split('onclick="loadmap("')[1].split(',"')[1].split('"')[0]
            if ".</div><div class=" in line2:
                hrs = (
                    line2.split('xs-4">')[1].split("<")[0]
                    + ": "
                    + line2.split('col-xs-8">')[1].split("<")[0]
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
