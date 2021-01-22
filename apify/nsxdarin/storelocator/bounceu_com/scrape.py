import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("bounceu_com")


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
    url = "https://www.bounceu.com/sitemap_url.xml"
    r = session.get(url, headers=headers)
    website = "bounceu.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "special-offers/</loc>" in line:
            locs.append(line.split("<loc>")[1].split("special-offers/</loc>")[0])
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
        hours = "<MISSING>"
        Closed = False
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'bu_store_ck-store_name">' in line2:
                name = line2.split('bu_store_ck-store_name">')[1].split("<")[0]
            if '<span itemprop="streetAddress">' in line2:
                add = line2.split('<span itemprop="streetAddress">')[1].split("<")[0]
                city = line2.split('="addressLocality">')[1].split("<")[0]
                state = line2.split('rop="addressRegion">')[1].split("<")[0]
                zc = line2.split('"postalCode">')[1].split("<")[0]
            if 'telephone" content="' in line2:
                phone = line2.split('telephone" content="')[1].split('"')[0]
            if "permanently closed" in line2:
                Closed = True
        if add != "" and Closed is False:
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
