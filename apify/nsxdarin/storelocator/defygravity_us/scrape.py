import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


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
    url = "http://www.defygravity.us/"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    website = "defygravity.us"
    typ = "<MISSING>"
    country = "US"
    store = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    for line in r.iter_lines(decode_unicode=True):
        if '<li><a href="http://www.' in line:
            locs.append(line.split('href="')[1].split('"')[0])
    for loc in locs:
        add = ""
        name = ""
        city = ""
        state = ""
        zc = ""
        phone = ""
        hours = ""
        HFound = False
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        lines = r2.iter_lines(decode_unicode=True)
        for line2 in lines:
            if "<title>" in line2 and name == "":
                name = line2.split("<title>")[1].split("<")[0]
                if "(" in name:
                    name = name.split("(")[0].strip()
            if '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
            if '<a href="https://maps.google.com/?q=' in line2 and "-->" not in line2:
                add = line2.split('">')[1].split("<")[0]
                city = line2.split("<br>")[1].split(",")[0]
                state = line2.split("<br>")[1].split(",")[1].strip().split(" ")[0]
                zc = line2.split("</a>")[0].rsplit(" ", 1)[1]
            if 'aria-labelledby="hours-menu">' in line2:
                HFound = True
            if HFound and "</ul>" in line2:
                HFound = False
            if HFound and "<li>" in line2:
                g = next(lines)
                h = next(lines)
                hrs = (
                    g.strip().replace("\r", "").replace("\t", "").replace("\n", "")
                    + ": "
                    + h.split("<")[0].strip().replace("\t", "")
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        if add != "":
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
    loc = "http://www.defygravity.us/durham"
    name = "DefyGravity Durham"
    add = "4300 Emperor Blvd, #250"
    city = "Durham"
    state = "NC"
    zc = "27703"
    phone = "919.825.1010"
    hours = "Temporarily Closed"
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
