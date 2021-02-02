import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("lubefast_com")


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
    urls = [
        "http://lubefast.com/oil-change-locations-alabama-florida-georgia-mississippi/oil-change-locations-mississippi/",
        "http://lubefast.com/oil-change-locations-alabama-florida-georgia-mississippi/oil-change-locations-florida/",
        "http://lubefast.com/oil-change-locations-alabama-florida-georgia-mississippi/oil-change-locations-alabama/",
        "http://lubefast.com/oil-change-locations-alabama-florida-georgia-mississippi/oil-change-locations-georgia/",
    ]
    website = "lubefast.com"
    typ = "<MISSING>"
    country = "US"
    for url in urls:
        logger.info(url)
        r = session.get(url, headers=headers)
        logger.info("Pulling Stores")
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '<h5><a href="http://lubefast.com/' in line:
                locs.append(line.split('href="')[1].split('"')[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = ""
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "American Lube Fast</strong><br />" in line2:
                name = ""
                add = ""
                city = ""
                state = ""
                zc = ""
                store = ""
                phone = ""
                lat = ""
                lng = ""
                hours = ""
                g = next(lines)
                h = next(lines)
                i = next(lines)
                g = str(g.decode("utf-8"))
                h = str(h.decode("utf-8"))
                i = str(i.decode("utf-8"))
                name = g.split("<")[0]
                if "Store #" in name:
                    store = name.split("#")[1].strip()
                    add = h.split("<")[0]
                    csz = i.split("<")[0].strip()
                else:
                    store = "<MISSING>"
                    add = g.split("<")[0]
                    csz = h.split("<")[0].strip()
                city = csz.split(",")[0]
                state = csz.split(",")[1].strip().split(" ")[0]
                state = state[:2]
                zc = csz.split(",")[1].strip()[-5:]
                if "-" in zc:
                    zc = csz.split(",")[1].strip()[-10:]
            if '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
            if "day<" in line2:
                hrs = line2.replace("<p>", "").replace("<br />", "")
                hrs = hrs.strip().replace("\t", "").replace("\n", "").replace("\r", "")
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if 'iframe src="https://www.google.com/maps/' in line2:
                lat = line2.split("!3d")[1].split("!")[0]
                lng = line2.split("!2d")[1].split("!")[0]
                if phone == "":
                    phone = "<MISSING>"
                if " " in state:
                    state = state.split(" ")[0]
                if "3250 W." in add:
                    phone = "8509412235"
                hours = hours + "; Sunday: Closed"
                name = "American Lube Fast"
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
