import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("redroof_com__hometowne-studios")


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
    url = "https://www.redroof.com/sitemap.xml"
    r = session.get(url, headers=headers)
    website = "redroof.com/hometowne-studios crawler"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>/extendedstay/hometownestudios/property/" in line:
            locs.append(
                "https://www.redroof.com" + line.split("<loc>")[1].split("<")[0]
            )
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = "<MISSING>"
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'Street1\\":\\"' in line2:
                add = line2.split('Street1\\":\\"')[1].split("\\")[0]
                zc = line2.split('"PostalCode\\":\\"')[1].split("\\")[0]
                state = line2.split('"State\\":\\"')[1].split("\\")[0]
                city = line2.split('"City\\":\\"')[1].split("\\")[0]
                lat = line2.split('"Latitude\\":\\"')[1].split("\\")[0]
                lng = line2.split('"Longitude\\":\\"')[1].split("\\")[0]
                phone = line2.split('"PhoneNumber\\":\\"')[1].split("\\")[0]
                name = line2.split('"Description\\":\\"')[1].split("\\")[0]
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
