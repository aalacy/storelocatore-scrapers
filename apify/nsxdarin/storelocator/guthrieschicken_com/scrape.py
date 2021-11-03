import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("guthrieschicken_com")


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
    url = "http://guthrieschicken.com/locations/"
    r = session.get(url, headers=headers)
    website = "guthrieschicken.com"
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
        if '<div class="col-md-6 mb-5 location" id="' in line:
            store = line.split('<div class="col-md-6 mb-5 location" id="')[1].split(
                '"'
            )[0]
        if "</span></h2>" in line:
            name = line.split("<span>")[1].split("<")[0]
            next(lines)
            g = next(lines)
            g = str(g.decode("utf-8"))
            add = g.split("|")[0].strip().replace("\t", "")
            csz = g.split("|")[1].split("<")[0].strip().replace("\t", "")
            city = csz.split(",")[0]
            state = csz.split(",")[1].strip().split(" ")[0]
            zc = csz.rsplit(" ", 1)[1]
            phone = (
                g.split("<p>")[1]
                .strip()
                .replace("\t", "")
                .replace("\r", "")
                .replace("\n", "")
            )
            next(lines)
            g = next(lines)
            g = str(g.decode("utf-8"))
            hours = (
                g.strip()
                .replace("\n", "")
                .replace("\r", "")
                .replace("<p>", "")
                .replace("<br/>", "; ")
                .replace("</p>", "")
            )
            g = next(lines)
            g = str(g.decode("utf-8"))
            if "pm" in g:
                hours = hours + "; " + g.split("<")[0]
            g = next(lines)
            g = str(g.decode("utf-8"))
            if "pm" in g:
                hours = hours + "; " + g.split("<")[0]
            if hours == "":
                hours = "<MISSING>"
            hours = hours.replace("<br>; Open", "Open")
        if '<a href="http://www.google.com/maps/?saddr=&daddr=' in line:
            lat = line.split('<a href="http://www.google.com/maps/?saddr=&daddr=')[
                1
            ].split(",")[0]
            lng = (
                line.split('<a href="http://www.google.com/maps/?saddr=&daddr=')[1]
                .split(",")[1]
                .split('"')[0]
            )
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
