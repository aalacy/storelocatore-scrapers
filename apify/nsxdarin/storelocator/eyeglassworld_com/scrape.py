import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("eyeglassworld_com")


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
    url = "https://www.eyeglassworld.com/store/store_sitemap.xml"
    r = session.get(url, headers=headers)
    website = "eyeglassworld.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>http://www.eyeglassworld.com/store-list/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
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
        try:
            r2 = session.get(loc, headers=headers)
            for line2 in r2.iter_lines():
                line2 = str(line2.decode("utf-8"))
                if '"name" : "' in line2:
                    name = line2.split('"name" : "')[1].split('"')[0]
                if '"streetAddress" : "' in line2:
                    add = line2.split('"streetAddress" : "')[1].split('"')[0]
                if '"addressLocality"  :  "' in line2:
                    city = line2.split('"addressLocality"  :  "')[1].split('"')[0]
                if '"addressRegion" : "' in line2:
                    state = line2.split('"addressRegion" : "')[1].split('"')[0]
                if '"postalCode" : "' in line2:
                    zc = line2.split('"postalCode" : "')[1].split('"')[0]
                if '"telephone" : "' in line2:
                    phone = line2.split('"telephone" : "')[1].split('"')[0]
                if 'pm"' in line2:
                    hrs = line2.split('"')[1]
                    if hours == "":
                        hours = hrs
                    else:
                        hours = hours + "; " + hrs
            if phone == "":
                phone = "<MISSING>"
            if hours == "":
                hours = "<MISSING>"
            add = (
                add.replace("Suite", " Suite").replace("  ", " ").replace("&amp;", "&")
            )
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
        except:
            pass


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
