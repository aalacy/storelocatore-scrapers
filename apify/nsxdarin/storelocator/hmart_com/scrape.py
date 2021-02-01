import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("hmart_com")


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
    url = "https://www.hmart.com/ourstores"
    r = session.get(url, headers=headers)
    website = "hmart.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<a href="https://www.hmart.com/storelocator/index/index/id/' in line:
            lurl = line.split('href="')[1].split('"')[0]
            if lurl not in locs:
                locs.append(lurl)
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
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<div class="location-header">' in line2:
                name = line2.split('<div class="location-header">')[1].split("<")[0]
            if add == "" and '"address":"' in line2:
                add = (
                    line2.split('"address":"')[1]
                    .split('"')[0]
                    .replace("Valley Road ", "Valley Road, ")
                    .replace("blvd.", "blvd.,")
                    .replace("HighwayFalls", "Highway, Falls")
                    .replace("Road.", "Road.,")
                    .replace("Balboa Ave", "Balboa Ave,")
                    .replace("HWYTORRANCE", "HWY, TORRANCE")
                    .replace("300 Duluth", "300, Duluth")
                    .replace("Rd.", "Rd.,")
                    .replace("85 Riverdale", "85, Riverdale")
                    .replace("Dr.", "Dr.,")
                    .replace("Road Schaumburg", "Road, Schaumburg")
                    .replace("Ave.", "Ave.,")
                    .replace("Pkwy.", "Pkwy.,")
                    .replace("St.", "St.,")
                    .replace("(Lincoln Highway)", "(Lincoln Highway),")
                    .replace("#130 ", "#130 ,")
                    .replace("Blvd.", "Bldv.,")
                    .replace(",,", ",")
                )
                zc = add.rsplit(" ", 1)[1]
                city = add.split(",")[1].strip()
                state = add.split(",")[2].strip().split(" ")[0]
                add = add.split(",")[0].strip()
                lat = line2.split('"lat":"')[1].split('"')[0]
                lng = line2.split('"lng":"')[1].split('"')[0]
                try:
                    phone = (
                        line2.split('"phone":"')[1]
                        .split('"')[0]
                        .replace("\\u2013", "-")
                    )
                except:
                    phone = "<MISSING>"
            if '{"item":{"id":"' in line2:
                store = line2.split('{"item":{"id":"')[1].split('"')[0]
            if "day:" in line2:
                day = (
                    line2.strip().replace("\t", "").replace("\n", "").replace("\r", "")
                )
            if " - " in line2 and "</td>" in line2:
                day = (
                    day
                    + ": "
                    + line2.strip()
                    .replace("\t", "")
                    .replace("\n", "")
                    .replace("\r", "")
                    .split("<")[0]
                )
                if hours == "":
                    hours = day
                else:
                    hours = hours + "; " + day
        hours = (
            hours.replace("\t", "")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("::", ":")
        )
        if hours == "" and "Northern 144" in name:
            hours = "Coming Soon"
        if "/58" in loc:
            zc = "21702"
        if "/34" in loc:
            zc = "08003"
        if "/53" in loc:
            zc = "11753"
        if "Carrollton" in name:
            add = "2625 Old Denton Rd. #200"
            city = "Carrollton"
            state = "TX"
        if "Duluth" in name:
            add = "2550 Pleasant Hill Rd. Bldg. 300"
            city = "Duluth"
            state = "GA"
        if "Doraville" in name:
            city = "Doraville"
            state = "GA"
            add = "6035 Peachtree Rd. Bldg B"
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
