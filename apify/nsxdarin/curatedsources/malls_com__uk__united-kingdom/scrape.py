import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("malls_com__uk__united-kingdom")


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
    url = "https://www.malls.com/sitemap_000.xml"
    r = session.get(url, headers=headers)
    website = "malls.com/uk/united-kingdom"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "https://www.malls.com/uk/malls/" in line and ".html" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = "<MISSING>"
        zc = ""
        store = "<MISSING>"
        phone = "<MISSING>"
        lat = ""
        lng = ""
        hours = "<MISSING>"
        rawadd = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                name = line2.split("<title>")[1].split("</title>")[0]
                if "<" in name:
                    name = name.split("<")[0]
                if " - " in name:
                    name = name.split(" - ")[0]
            if 'latitude" content="' in line2:
                lat = line2.split('latitude" content="')[1].split('"')[0]
            if 'longitude" content="' in line2:
                lng = line2.split('longitude" content="')[1].split('"')[0]
            if '<div class="r"><b>' in line2:
                rawadd = line2.split('<div class="r"><b>')[1].split("<")[0]
                addr = parse_address_intl(rawadd)
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
