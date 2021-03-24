import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("giuntasmeatfarms_com")


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
    url = "https://giuntasmeatfarms.com/locations/"
    coords = []
    r = session.get(url, headers=headers)
    website = "giuntasmeatfarms.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    store = "<MISSING>"
    hours = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    logger.info("Pulling Stores")
    lines = r.iter_lines()
    for line in lines:
        line = str(line.decode("utf-8"))
        if '<div class="marker"' in line:
            llat = line.split('data-lat="')[1].split('"')[0]
            llng = line.split('data-lng="')[1].split('"')[0]
            g = next(lines)
            g = str(g.decode("utf-8"))
            lname = g.split(">")[1].split("<")[0].strip()
            coords.append(lname + "|" + llat + "|" + llng)
        if '<div class="location_title">' in line:
            g = next(lines)
            g = str(g.decode("utf-8"))
            name = g.split("<")[0].strip().replace("\t", "")
        if '<div class="location_address">' in line:
            g = next(lines)
            g = str(g.decode("utf-8"))
            add = g.split(">")[1].split("<")[0].replace(",", "").strip()
            g = next(lines)
            g = str(g.decode("utf-8"))
            csz = g.split("<")[0].strip()
            city = g.split(",")[0]
            state = g.split(",")[1].strip().split(" ")[0]
            zc = g.rsplit(" ", 1)[1].split("<")[0]
        if '<a href="tel:' in line:
            phone = line.split('<a href="tel:')[1].split('"')[0]
        if "Store Hours" in line:
            next(lines)
            g = next(lines)
            g = str(g.decode("utf-8"))
            hours = g.split("<")[0].strip().replace("\t", "")
            g = next(lines)
            g = str(g.decode("utf-8"))
            hours = hours + "; " + g.split("<")[0].strip().replace("\t", "")
            for coord in coords:
                if name == coord.split("|")[0]:
                    lat = coord.split("|")[1]
                    lng = coord.split("|")[2]
            loc = "https://giuntasmeatfarms.com/locations/"
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
