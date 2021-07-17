import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("crackerbarrel_com")


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
    url = "https://www.crackerbarrel.com/sitemap.xml"
    r = session.get(url, headers=headers)
    website = "crackerbarrel.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://crackerbarrel.com/Locations/States/" in line:
            lurl = line.split("<loc>")[1].split("<")[0]
            if lurl.count("/") == 7:
                locs.append(lurl)
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = loc.rsplit("/", 1)[1]
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '"address1":"' in line2:
                add = line2.split('"address1":"')[1].split('"')[0]
            if '"city":"' in line2:
                city = line2.split('"city":"')[1].split('"')[0]
                state = line2.split('"state":"')[1].split('"')[0]
                name = "Cracker Barrel in " + city + ", " + state
                zc = line2.split('"zip":"')[1].split('"')[0]
                lat = line2.split('latitude":"')[1].split('"')[0]
                lng = line2.split('longitude":"')[1].split('"')[0]
                phone = line2.split('"phone":"')[1].split('"')[0]
                hours = (
                    "Sun: "
                    + line2.split('"Sunday_Open":{"value":"')[1].split('"')[0]
                    + "-"
                    + line2.split('"Sunday_Close":{"value":"')[1].split('"')[0]
                )
                hours = (
                    hours
                    + "; Mon: "
                    + line2.split('"Monday_Open":{"value":"')[1].split('"')[0]
                    + "-"
                    + line2.split('"Monday_Close":{"value":"')[1].split('"')[0]
                )
                hours = (
                    hours
                    + "; Mon: "
                    + line2.split('"Tuesday_Open":{"value":"')[1].split('"')[0]
                    + "-"
                    + line2.split('"Tuesday_Close":{"value":"')[1].split('"')[0]
                )
                hours = (
                    hours
                    + "; Mon: "
                    + line2.split('"Wednesday_Open":{"value":"')[1].split('"')[0]
                    + "-"
                    + line2.split('"Wednesday_Close":{"value":"')[1].split('"')[0]
                )
                hours = (
                    hours
                    + "; Mon: "
                    + line2.split('"Thursday_Open":{"value":"')[1].split('"')[0]
                    + "-"
                    + line2.split('"Thursday_Close":{"value":"')[1].split('"')[0]
                )
                hours = (
                    hours
                    + "; Mon: "
                    + line2.split('"Friday_Open":{"value":"')[1].split('"')[0]
                    + "-"
                    + line2.split('"Friday_Close":{"value":"')[1].split('"')[0]
                )
                hours = (
                    hours
                    + "; Mon: "
                    + line2.split('"Saturday_Open":{"value":"')[1].split('"')[0]
                    + "-"
                    + line2.split('"Saturday_Close":{"value":"')[1].split('"')[0]
                )
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
