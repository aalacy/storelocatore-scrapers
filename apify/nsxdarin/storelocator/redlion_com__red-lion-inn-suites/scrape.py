import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("redlion_com__red-lion-inn-suites")

session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
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
    url = "https://www.redlion.com/sitemap.xml"
    locs = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://www.redlion.com/red-lion-inn-suites/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
    for loc in locs:
        logger.info(("Pulling Location %s..." % loc))
        loc2 = (
            loc.replace("www.redlion.com/", "www.redlion.com/page-data/")
            + "/page-data.json"
        )
        r2 = session.get(loc2, headers=headers)
        website = "redlion.com/red-lion-inn-suites"
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '{"hotel":{"name":"' in line2:
                name = line2.split('{"hotel":{"name":"')[1].split('"')[0]
                country = line2.split('"country_code":"')[1].split('"')[0]
                store = line2.split('"crs_code":"')[1].split('"')[0]
                phone = line2.split('"phone":"')[1].split('"')[0]
                add = line2.split('"address_line1":"')[1].split('"')[0]
                city = line2.split('"locality":"')[1].split('"')[0]
                state = line2.split('"administrative_area":"')[1].split('"')[0]
                zc = line2.split('"postal_code":"')[1].split('"')[0]
                lat = line2.split('{"lat":')[1].split(",")[0]
                lng = line2.split('"lon":')[1].split("}")[0]
                hours = "<MISSING>"
                typ = "Red Lion Inn & Suites"
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
