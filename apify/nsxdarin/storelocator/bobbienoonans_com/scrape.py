import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("bobbienoonans_com")


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
    states = []
    url = "http://www.bobbienoonans.com/"
    r = session.get(url, headers=headers)
    website = "bobbienoonans.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if (
            'href="http://www.bobbienoonans.com/locations/' in line
            and ">Locations" not in line
        ):
            states.append(line.split('href="')[1].split('"')[0])
    for state in states:
        logger.info(state)
        r2 = session.get(state, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if (
                '<div class="one-half">' in line2
                or 'div class="one-half first">' in line2
            ):
                if '<a href="' in line2:
                    name = line2.split('href="')[1].split(">")[1].split("<")[0]
                    loc = (
                        "http://www.bobbienoonans.com"
                        + line2.replace("<strong>", "")
                        .split('<a href="')[1]
                        .split('"')[0]
                    )
                    g = next(lines)
                    h = next(lines)
                    i = next(lines)
                    g = str(g.decode("utf-8"))
                    h = str(h.decode("utf-8"))
                    i = str(i.decode("utf-8"))
                    add = g.split("<")[0]
                    city = h.split(",")[0]
                    state = h.split(",")[1].strip().split(" ")[0]
                    zc = h.split("<")[0].strip().rsplit(" ", 1)[1]
                    phone = i.split("P:")[1].split("<")[0].strip()
                    lat = "<MISSING>"
                    lng = "<MISSING>"
                    store = "<MISSING>"
                    hours = "<MISSING>"
                    if "cape-coral-academy" in loc:
                        name = "Cape Coral Academy"
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
            if (
                '<a href="/bobbienoonan/' in line2
                or '<a href="http://www.noonanacademy.org/">' in line2
            ):
                loc = line2.split('href="')[1].split('/"')[0]
                if "bobbienoonan" in loc:
                    loc = "http://www.bobbienoonans.com/" + loc.rsplit("/", 1)[1]
                name = line2.split('href="')[1].split(">")[1].split("<")[0]
                g = next(lines)
                g = str(g.decode("utf-8"))
                if "Day Care" in g:
                    g = next(lines)
                    g = str(g.decode("utf-8"))
                h = next(lines)
                i = next(lines)
                h = str(h.decode("utf-8"))
                i = str(i.decode("utf-8"))
                h = h.replace("Park IL", "Park, IL")
                add = g.replace("<p>", "").split("<")[0]
                city = h.split(",")[0]
                state = h.split(",")[1].strip().split(" ")[0]
                zc = h.split("<")[0].strip().rsplit(" ", 1)[1]
                phone = i.split("P:")[1].split("<")[0].strip()
                g = next(lines)
                g = next(lines)
                g = str(g.decode("utf-8"))
                lat = "<MISSING>"
                lng = "<MISSING>"
                store = "<MISSING>"
                hours = "<MISSING>"
                if "p.m" in g:
                    hours = g.split("<")[0].strip()
                else:
                    hours = "<MISSING>"
                if "ALSIP" in name:
                    loc = "http://www.bobbienoonans.com/alsip/"
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
