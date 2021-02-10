import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("cottonpatch_com")


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
    url = "https://cottonpatch.com/locations/"
    r = session.get(url, headers=headers)
    website = "cottonpatch.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if (
            '<a href="https://cottonpatch.com/locations/' in line
            and '<div class="location-state-group"' in line
        ):
            items = line.split('<a href="https://cottonpatch.com/locations/')
            for item in items:
                if "<span></span></a></div>" in item:
                    locs.append(
                        "https://cottonpatch.com/locations/" + item.split('"')[0]
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
        HFound = False
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                name = line2.split("<title>")[1].split("<")[0].replace("&#8211;", "-")
            if add == "" and '<p class="distance">' in line2:
                g = next(lines)
                g = str(g.decode("utf-8"))
                add = g.split("<")[0].strip().replace("\t", "")
                city = g.split(">")[1].split(",")[0]
                state = g.split(">")[1].split(",")[1].strip().split(" ")[0]
                zc = g.split(">")[1].split("<")[0].rsplit(" ", 1)[1]
            if phone == "" and '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
            if lat == "" and 'class="row map" data-coords="' in line2:
                lat = line2.split('class="row map" data-coords="')[1].split(",")[0]
                lng = (
                    line2.split('class="row map" data-coords="')[1]
                    .split(",")[1]
                    .split('"')[0]
                )
            if "<p>Hours:<br/>" in line2 and hours == "":
                HFound = True
            if HFound and "Menu" in line2:
                HFound = False
            if HFound and "pm<" in line2:
                hrs = line2.split("<")[0].strip()
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
