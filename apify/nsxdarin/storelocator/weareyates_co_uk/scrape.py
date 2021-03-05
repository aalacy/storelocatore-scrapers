import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("weareyates_co_uk")


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
    url = "https://www.weareyates.co.uk/find-a-pub"
    r = session.get(url, headers=headers)
    website = "weareyates.co.uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'class="inner-item">' in line:
            locs.append(
                "https://www.weareyates.co.uk" + line.split('href="')[1].split('"')[0]
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
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        DFound = True
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if 'href="tel:' in line2 and phone == "":
                phone = line2.split('href="tel:')[1].split('"')[0]
            if '<h1 class="section-heading">Welcome to <br />' in line2:
                name = line2.split('<h1 class="section-heading">Welcome to <br />')[
                    1
                ].split("<")[0]
            if 'menu vertical address">' in line2:
                g = next(lines)
                h = next(lines)
                i = next(lines)
                j = next(lines)
                g = str(g.decode("utf-8"))
                h = str(h.decode("utf-8"))
                i = str(i.decode("utf-8"))
                j = str(j.decode("utf-8"))
                state = "<MISSING>"
                if "<li>" not in j:
                    add = g.split(">")[1].split("<")[0]
                    city = h.split(">")[1].split("<")[0]
                    zc = i.split(">")[1].split("<")[0]
                else:
                    add = (
                        g.split(">")[1].split("<")[0]
                        + " "
                        + h.split(">")[1].split("<")[0]
                    )
                    city = i.split(">")[1].split("<")[0]
                    zc = j.split(">")[1].split("<")[0]
            if DFound and '<div class="address">' in line2:
                DFound = False
            if DFound and "day: </span>" in line2:
                hrs = line2.split(">")[1].split("<")[0]
                next(lines)
                g = next(lines)
                g = str(g.decode("utf-8"))
                hrs = hrs + g.strip().replace("\t", "").replace("\r", "").replace(
                    "\n", ""
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if "center: { lng:" in line2:
                lng = line2.split("center: { lng:")[1].split(",")[0].strip()
                lat = line2.split("lat: ")[1].split("}")[0].strip()
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
