import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("budgethost_com")


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
    url = "http://budgethost.com/hotelsearch.aspx"
    r = session.get(url, headers=headers)
    website = "budgethost.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    HFound = False
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "SELECT A STATE OR HOTEL" in line:
            HFound = True
        if HFound and "</select>" in line:
            HFound = False
        if HFound and '.aspx">' in line:
            lurl = (
                "http://budgethost.com/hotels/" + line.split('value="')[1].split('"')[0]
            )
            lname = line.split('">')[1].split("<")[0]
            locs.append(lurl + "|" + lname)
    for loc in locs:
        logger.info(loc)
        name = loc.split("|")[1]
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = "<MISSING>"
        lng = "<MISSING>"
        hours = "<MISSING>"
        lurl = loc.split("|")[0]
        r2 = session.get(lurl, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "</h1>" in line2:
                g = next(lines)
                g = (
                    str(g.decode("utf-8"))
                    .replace("<p>", "")
                    .replace("</p>", "")
                    .strip()
                    .replace("\t", "")
                )
                if g.count(",") == 2:
                    add = g.split(",")[0]
                    city = g.split(",")[1].strip()
                    state = g.split(",")[2].strip().split(" ")[0]
                    zc = g.rsplit(" ", 1)[1]
                else:
                    add = g.split(",")[0] + " " + g.split(",")[1].strip()
                    city = g.split(",")[2].strip()
                    state = g.split(",")[3].strip().split(" ")[0]
                    zc = g.rsplit(" ", 1)[1]
            if "P: " in line2:
                phone = line2.split("P: ")[1].split("<")[0].strip()
        name = name.replace("&#39;", "'")
        if phone == "":
            phone = "<MISSING>"
        if "OH" in zc:
            zc = "<MISSING>"
        yield [
            website,
            lurl,
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
