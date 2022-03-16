import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("ukmalls_co_uk__shopping-centres")


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
    url = "https://www.ukmalls.co.uk/shopping-centres"
    r = session.get(url, headers=headers)
    website = "ukmalls.co.uk/shopping-centres"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    lines = r.iter_lines()
    for line in lines:
        line = str(line.decode("utf-8"))
        if '<div class="listing-item-container list-layout letter-show letter-' in line:
            g = next(lines)
            g = str(g.decode("utf-8"))
            locs.append(g.split('href="')[1].split('"')[0])
    for loc in locs:
        if "/" in loc:
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
            lines2 = r2.iter_lines()
            for line2 in lines2:
                line2 = str(line2.decode("utf-8"))
                if "<h1>" in line2:
                    name = line2.split("<h1>")[1].split("<")[0].strip()
                if '"latitude": ' in line2:
                    lat = line2.split('"latitude": ')[1].split(",")[0]
                if '"longitude": ' in line2:
                    lng = line2.split('"longitude": ')[1].split("}")[0].strip()
                if '"telephone": "' in line2:
                    if "london/the-broadwalk-centre" in loc:
                        phone = "020 8905 6303"
                    else:
                        phone = line2.split('"telephone": "')[1].split('"')[0]
                if "Country:</th>" in line2:
                    g = next(lines2)
                    g = str(g.decode("utf-8"))
                    if '">' in g:
                        state = g.split('">')[1].split("<")[0]
                    else:
                        g = next(lines2)
                        g = str(g.decode("utf-8"))
                        state = g.split('">')[1].split("<")[0]
                if "City:</th>" in line2:
                    g = next(lines2)
                    g = str(g.decode("utf-8"))
                    city = g.split('">')[1].split("<")[0]
                if 'data-id="' in line2:
                    store = line2.split('data-id="')[1].split('"')[0]
                if '"postalCode": "' in line2:
                    zc = line2.split('"postalCode": "')[1].split('"')[0]
                    zc = zc[:8]
                if '"streetAddress": "' in line2:
                    add = line2.split('"streetAddress": "')[1].split('"')[0]
                if '"dayOfWeek": [ "' in line2:
                    day = line2.split('"dayOfWeek": [ "')[1].split('"')[0]
                if '"opens": "' in line2:
                    hrs = day + ": " + line2.split('"opens": "')[1].split('"')[0]
                if '"closes": "' in line2:
                    hrs = hrs + "-" + line2.split('"closes": "')[1].split('"')[0]
                    if hours == "":
                        hours = hrs
                    else:
                        hours = hours + "; " + hrs
            if hours == "":
                hours = "<MISSING>"
            if add == "":
                add = "<MISSING>"
            if zc == "":
                zc = "<MISSING>"
            if phone == "" or "Not Available" in phone:
                phone = "<MISSING>"
            if store == "":
                store = "<MISSING>"
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
