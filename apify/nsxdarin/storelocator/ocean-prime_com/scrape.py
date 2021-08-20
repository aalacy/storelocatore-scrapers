import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("ocean-prime_com")


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
    locs = ["https://www.ocean-prime.com/Locations-menus/Naples"]
    url = "https://www.ocean-prime.com/locations"
    r = session.get(url, headers=headers)
    website = "ocean-prime.com"
    typ = "<MISSING>"
    country = "US"
    coord = []
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if (
            '<h2><a href="/Locations/' in line
            or '<h2><a href="/locations-menus/' in line
        ):
            locs.append(
                "https://www.ocean-prime.com" + line.split('href="')[1].split('"')[0]
            )
        if "/@" in line:
            llat = line.split("/@")[1].split(",")[0]
            llng = line.split("/@")[1].split(",")[1]
            title = line.split('target="_blank">')[1].split("<")[0].strip()
            coord.append(title + "|" + llat + "|" + llng)
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = "<MISSING>"
        lng = "<MISSING>"
        hours = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if '<a class="navbar-brand" href="#">' in line2:
                name = line2.split('<a class="navbar-brand" href="#">')[1].split("<")[0]
            if "LOCATION</h2>" in line2 and "Naples" not in loc:
                next(lines)
                g = next(lines)
                g = str(g.decode("utf-8"))
                if "</strong>" in g:
                    g = next(lines)
                    g = str(g.decode("utf-8"))
                add = g.split("<br />")[0]
                if ">" in add:
                    add = add.split(">")[1]
                g = next(lines)
                g = str(g.decode("utf-8"))
                city = g.split(",")[0]
                zc = g.split("<")[0].rsplit(" ", 1)[1]
                state = g.split(",")[1].strip().split(" ")[0]
            if '<a href="tel://' in line2:
                phone = line2.split('<a href="tel://')[1].split('"')[0]
            if "day</strong>" in line2 or "day </strong>" in line2:
                hrs = (
                    line2.replace("\r", "").replace("\t", "").replace("\n", "").strip()
                )
                hrs = (
                    hrs.replace("<br />", "")
                    .replace("<strong>", "")
                    .replace("</strong>", "; ")
                    .replace("&nbsp;", "")
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        if "Naples" in loc:
            add = "699 5th Avenue South"
            city = "Naples"
            state = "FL"
            zc = "34102"
        hours = hours.replace("<p>", "").replace("</p>", "")
        add = add.replace("&nbsp;", " ")
        name = name.replace("&nbsp;", " ")
        hours = hours.replace("&amp;", "&")
        if "</p></div>" in hours:
            hours = hours.split("</p></div>")[0]
        if phone == "":
            phone = "<MISSING>"
        if "Manhattan" in loc:
            hours = "MONDAY-THURSDAY: 4 PM - 9 PM; FRIDAY: 4 PM - 10 PM; SATURDAY: 4 PM - 10 PM; SUNDAY: 4 PM - 9 PM"
        if "Orlando-Rialto" in loc:
            hours = "MONDAY-SUNDAY: 5PM - 9PM"
        if "Naples" in loc:
            hours = "SUNDAY - THURSDAY: 4PM - 9PM; FRIDAY & SATURDAY: 4PM - 10PM"
        lname = city + ", " + state
        for item in coord:
            if item.split("|")[0] == lname:
                lat = item.split("|")[1]
                lng = item.split("|")[2]
        if "Detroit" in name:
            lat = "42.55915"
            lng = "-83.192967"
        if "Larimer Square" in name:
            lat = "39.7482802"
            lng = "-104.9990006"
        if "Tampa" in name:
            lat = "27.953844"
            lng = "-82.539328"
        if "New York City" in name:
            lat = "40.76173"
            lng = "-73.98063"
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
