import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("muffinbreak_co_uk")


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
                "raw_address",
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
    url = "https://muffinbreak.co.uk/store-sitemap.xml"
    r = session.get(url, headers=headers)
    website = "muffinbreak.co.uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://muffinbreak.co.uk/store/" in line:
            locs.append(line.split(">")[1].split("<")[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        zc = "<MISSING>"
        rawadd = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if '<h1 style="margin-bottom: 0;">' in line2:
                name = line2.split('<h1 style="margin-bottom: 0;">')[1].split("<")[0]
            if "T: <strong>" in line2:
                phone = line2.split("T: <strong>")[1].split("<")[0].strip()
            if "center=" in line2:
                lat = line2.split("center=")[1].split(",")[0]
                lng = line2.split("center=")[1].split(",")[1].split("&")[0]
                next(lines)
                g = next(lines)
                g = str(g.decode("utf-8"))
                if "T: <strong>" in g:
                    phone = g.split("T: <strong>")[1].split("<")[0]
                if "bexleyheath" not in loc:
                    rawadd = g.split("<p>")[1].split("</p>")[0]
                    if "<br" in rawadd:
                        rawadd = rawadd.split("<br")[0]
                    rawadd = rawadd.strip().replace("\t", "")
            if "day</th>" in line2:
                hrs = line2.split(">")[1].split("<")[0]
                g = next(lines)
                g = str(g.decode("utf-8"))
                hrs = hrs + ": " + g.split(">")[1].split("<")[0].replace("&#8211;", "-")
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        if phone == "":
            phone = "<MISSING>"
        if "bexleyheath-broadway" in loc:
            rawadd = "Unit 2, 131 Broadway Bexleyheath Kent"
        if name != "":
            add = add.replace("&#8217;", "'")
            if lat == "":
                lat = "<MISSING>"
                lng = "<MISSING>"
            yield [
                website,
                loc,
                name,
                rawadd,
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
