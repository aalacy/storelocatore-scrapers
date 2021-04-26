import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("maceys_com__pharmacy")


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
    url = "https://maceys.com/pharm/locations"
    locs = []
    r = session.get(url, headers=headers)
    website = "maceys.com/pharmacy"
    typ = "<MISSING>"
    country = "US"
    store = "<MISSING>"
    hours = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    logger.info("Pulling Stores")
    Found = False
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'Locations <i class="' in line:
            Found = True
        if Found and "</ul>" in line:
            Found = False
        if Found and '<a href="' in line and 'Locations <i class="' not in line:
            locs.append("https://maceys.com" + line.split('href="')[1].split('"')[0])
    for loc in locs:
        logger.info(loc)
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        phone = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        name = ""
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                name = line2.split("<title>")[1].split("<")[0]
            if "Pharmacy Phone Number:</h5>" in line2:
                next(lines)
                g = next(lines)
                g = str(g.decode("utf-8"))
                phone = g.split('<a href="tel:')[1].split('"')[0]
            if "Address:</h5>" in line2:
                next(lines)
                g = next(lines)
                h = next(lines)
                g = str(g.decode("utf-8"))
                h = str(h.decode("utf-8"))
                add = g.split("<")[0].strip().replace("\t", "")
                city = g.split(">")[1].split(",")[0].strip()
                zc = h.split(";")[1].split("<")[0].strip().replace("\t", "")
                state = h.split("&")[0].strip().replace("\t", "")
        name = name.replace("Macey's - ", "")
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
