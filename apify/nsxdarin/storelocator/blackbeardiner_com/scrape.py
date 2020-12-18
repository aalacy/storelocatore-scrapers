import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("blackbeardiner_com")


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
    url = "https://blackbeardiner.com/locations/"
    r = session.get(url, headers=headers)
    website = "blackbeardiner.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'name="store link" href="' in line:
            locs.append(line.split('name="store link" href="')[1].split('"')[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        phone = ""
        lat = ""
        lng = ""
        store = "<MISSING>"
        hours = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                name = line2.split("<title>")[1].split(" |")[0]
                if "<" in name:
                    name = name.split("<")[0]
                name = name.replace("Black Bear Diner Location", "").strip()
            if "<address>" in line2:
                g = next(lines)
                h = next(lines)
                i = next(lines)
                g = str(g.decode("utf-8"))
                h = str(h.decode("utf-8"))
                i = str(i.decode("utf-8"))
                add = g.split("<")[0].strip().replace("\t", "")
                city = h.split(",")[0].strip().replace("\t", "")
                state = h.split(",")[1].split("\t")[0].strip()
                zc = h.rsplit("\t", 1)[1].split("<")[0].strip()
                phone = i.split("<")[0].strip().replace("\t", "")
            if "center: {lat: " in line2:
                lat = line2.split("center: {lat: ")[1].split(",")[0]
                lng = line2.split("lng:")[1].split("}")[0].strip()
            if "day:<" in line2 or "Daily:" in line2:
                hrs = (
                    line2.replace("<div class='store_hours'>", "")
                    .replace("</div>", "")
                    .replace("<br />", "")
                    .replace("<p>", "")
                    .replace("</span>", "")
                    .replace("</p>", "")
                    .replace("</span>", "")
                    .replace('<span class="hours-split-2">', "")
                    .strip()
                    .replace("\r", "")
                    .replace("\n", "")
                    .replace("\t", "")
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
