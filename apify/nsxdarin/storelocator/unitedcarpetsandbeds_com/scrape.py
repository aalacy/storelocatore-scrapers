import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("unitedcarpetsandbeds_com")


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
    url = "https://www.unitedcarpetsandbeds.com/storelocator/"
    r = session.get(url, headers=headers)
    website = "unitedcarpetsandbeds.com"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'href="https://www.unitedcarpetsandbeds.com/storelocator/' in line:
            locs.append(line.split('href="')[1].split('"')[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = "<MISSING>"
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        HFound = True
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if ">More Details</a>" in line2:
                HFound = False
            if HFound and "day</span>" in line2:
                day = line2.split(">")[1].split("<")[0]
            if HFound and 'cell -time">' in line2:
                hrs = day + ": " + line2.split('cell -time">')[1].split("<")[0]
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if '="item location_page">' in line2:
                g = next(lines)
                g = str(g.decode("utf-8"))
                name = g.split(">")[1].split("<")[0]
            if ">Street address: </span>" in line2:
                g = next(lines)
                g = str(g.decode("utf-8"))
                add = g.split(">")[1].split("<")[0]
            if "City: </span>" in line2:
                g = next(lines)
                g = str(g.decode("utf-8"))
                city = g.split(">")[1].split("<")[0]
            if "Postcode: </span>" in line2:
                g = next(lines)
                g = str(g.decode("utf-8"))
                zc = g.split(">")[1].split("<")[0]
            if '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
            if "lat: " in line2:
                lat = line2.split("lat: ")[1].split(",")[0]
            if "lng: " in line2:
                lng = line2.split("lng: ")[1].split(",")[0]
        if "(" in add:
            add = add.split("(")[0].strip()
        name = name.replace("&#039;", "'")
        add = add.replace("&#039;", "'")
        city = city.replace("&#039;", "'")
        name = name.replace("&amp;", "&")
        city = city.replace("&amp;", "&")
        add = add.replace("&amp;", "&")
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
