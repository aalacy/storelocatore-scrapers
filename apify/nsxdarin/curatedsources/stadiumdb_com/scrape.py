import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("stadiumdb_com")


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
        "http://stadiumdb.com/stadiums/eng",
        "http://stadiumdb.com/stadiums/nir",
        "http://stadiumdb.com/stadiums/sco",
        "http://stadiumdb.com/stadiums/wal",
    ]
    website = "stadiumdb.com"
    typ = "<MISSING>"
    country = "GB"
    for url in urls:
        r = session.get(url, headers=headers)
        logger.info(url)
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '<a href="http://stadiumdb.com/stadiums/' in line:
                lurl = line.split('href="')[1].split('"')[0]
                if lurl not in locs:
                    locs.append(lurl)
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = loc.split("/stadiums/")[1].split("/")[0].upper()
        zc = ""
        store = "<MISSING>"
        phone = "<MISSING>"
        lat = "<MISSING>"
        lng = "<MISSING>"
        hours = "<MISSING>"
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if '<h1 class="icon i-stadium">' in line2:
                name = line2.split('<h1 class="icon i-stadium">')[1].split("<")[0]
            if "Address</th>" in line2:
                g = next(lines)
                g = str(g.decode("utf-8"))
                addinfo = (
                    g.split("<td>")[1]
                    .split("</td>")[0]
                    .strip()
                    .replace(", United Kingdom", "")
                )
                addr = parse_address_intl(addinfo)
                city = addr.city
                zc = addr.postcode
                add = addr.street_address_1
        if city == "" or city is None:
            city = "<MISSING>"
        if zc == "" or zc is None:
            zc = "<MISSING>"
        if add == "" or add is None:
            add = "<MISSING>"
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
