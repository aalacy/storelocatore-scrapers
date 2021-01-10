import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("jimmysegg_com")


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
    url = "https://www.jimmysegg.com/online-ordering/"
    r = session.get(url, headers=headers)
    website = "jimmysegg.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "ORDER NOW<" in line:
            locs.append(line.split('href="')[1].split('"')[0])
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
        HFound = False
        hours = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "Hours of Business</div>" in line2:
                HFound = True
            if HFound and "carryout" in line2:
                HFound = False
            if HFound and '<div class="hours-day">' in line2:
                g = next(lines)
                g = str(g.decode("utf-8"))
                day = g.split("<")[0].strip().replace("\t", "")
            if HFound and '<div class="hours-time">' in line2:
                g = next(lines)
                g = str(g.decode("utf-8"))
                day = (
                    day
                    + ": "
                    + g.replace("\r", "").replace("\t", "").replace("\n", "").strip()
                )
                if hours == "":
                    hours = day
                else:
                    hours = hours + "; " + day
            if '"name": "' in line2:
                name = line2.split('"name": "')[1].split('"')[0].replace("\\u0027", "'")
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if '"latitude": "' in line2:
                lat = line2.split('"latitude": "')[1].split('"')[0]
            if '"longitude": "' in line2:
                lng = line2.split('"longitude": "')[1].split('"')[0]
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if '<h1 class="restaurant-name">' in line2:
                name = (
                    line2.split('<h1 class="restaurant-name">')[1]
                    .split("<")[0]
                    .strip()
                    .replace("&#39;", "'")
                )
            if "var _locationLat = " in line2:
                lat = line2.split("var _locationLat = ")[1].split(";")[0]
            if "var _locationLng = " in line2:
                lng = line2.split("var _locationLng = ")[1].split(";")[0]
            if 'var _locationAddress = "' in line2:
                addinfo = line2.split('var _locationAddress = "')[1].split('"')[0]
                add = addinfo.split(",")[0]
                zc = addinfo.split(",")[2].rsplit(" ", 1)[1]
                city = addinfo.split(",")[1].strip()
                state = addinfo.split(",")[2].strip().split(" ")[0]
            if '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
        name = name.replace("\\u0026", "&")
        if hours == "":
            hurl = loc.replace("/#", "") + "/Website/Hours"
            r3 = session.get(hurl, headers=headers)
            lines2 = r3.iter_lines()
            for line3 in lines2:
                line3 = str(line3.decode("utf-8"))
                if "day</td>" in line3:
                    day = line3.split(">")[1].split("<")[0]
                if '"text-right">' in line3:
                    if '<td class="text-right">Closed' in line3:
                        day = day + ": Closed"
                    else:
                        g = next(lines2)
                        g = str(g.decode("utf-8"))
                        day = (
                            day
                            + ": "
                            + g.replace("\r", "")
                            .replace("\t", "")
                            .replace("\n", "")
                            .strip()
                        )
                        if hours == "":
                            hours = day
                        else:
                            hours = hours + "; " + day
        if "3948 S Peoria" in add:
            hours = "Monday-Friday: 7:00AM-1:00PM, Saturday and Sunday: 6:00AM-2:00PM"
        if "1616 N May Ave" in add:
            hours = "Monday - Sunday: 6:30 AM - 2:00 PM"
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
    loc = "<MISSING>"
    name = "McAllen, TX"
    add = "4100 N. 10th St."
    city = "McAllen"
    state = "TX"
    zc = "78504"
    phone = "<MISSING>"
    hours = "Sun-Sat: 6am-2pm"
    lat = "<MISSING>"
    lng = "<MISSING>"
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
    loc = "<MISSING>"
    name = "Mission, TX"
    add = "614 N. Shary Road"
    city = "Mission"
    state = "TX"
    zc = "78572"
    phone = "<MISSING>"
    hours = "Sun-Sat: 6am-2pm"
    lat = "<MISSING>"
    lng = "<MISSING>"
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
