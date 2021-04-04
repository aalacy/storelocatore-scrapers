import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("econolube_com")


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
    url = "https://www.econolube.com/page-sitemap.xml"
    r = session.get(url, headers=headers)
    website = "econolube.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://www.econolube.com/locations/" in line and "-" in line:
            lurl = line.split("<loc>")[1].split("<")[0]
            if (
                "0" in lurl
                or "1" in lurl
                or "2" in lurl
                or "3" in lurl
                or "4" in lurl
                or "5" in lurl
                or "6" in lurl
                or "7" in lurl
                or "8" in lurl
                or "9" in lurl
            ):
                locs.append(line.split("<loc>")[1].split("<")[0])
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
            if "<h1>" in line2:
                name = line2.split("<h1>")[1].split("<")[0]
            if '"streetAddress":"' in line2:
                add = line2.split('"streetAddress":"')[1].split('"')[0]
                phone = line2.split('"telephone":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                state = line2.split('"addressRegion":"')[1].split('"')[0]
                city = line2.split('"addressLocality":"')[1].split('"')[0]
                hours = (
                    line2.split(',"openingHours":["')[1]
                    .split('"]')[0]
                    .replace('","', "; ")
                )
            if 'data-center="{latitude: ' in line2:
                lat = line2.split('data-center="{latitude: ')[1].split(",")[0]
                lng = line2.split("longitude: ")[1].split("}")[0].strip()
            if 'data-storeid="' in line2 and store == "":
                store = line2.split('data-storeid="')[1].split('"')[0]
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
