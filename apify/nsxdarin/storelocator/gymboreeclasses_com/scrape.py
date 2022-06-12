import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("gymboreeclasses_com")


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
    url = "https://www.gymboreeclasses.com/sitemap.xml"
    r = session.get(url, headers=headers)
    website = "gymboreeclasses.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if (
            "><loc>https://www.gymboreeclasses.com/en/locations/" in line
            and ".html" not in line
        ):
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
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = "<MISSING>"
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '"shortName":"' in line2:
                name = line2.split('"shortName":"')[1].split('"')[0]
            if '"street1":"' in line2:
                add = line2.split('"street1":"')[1].split('"')[0]
                phone = line2.split('"telephone1":"')[1].split('"')[0]
                state = line2.split('"state":"')[1].split('"')[0]
                city = name
                zc = line2.split('"zip":"')[1].split('"')[0]
                try:
                    lat = line2.split('"lat":')[1].split(",")[0]
                    lng = line2.split('"lng":')[1].split(",")[0]
                except:
                    lat = "<MISSING>"
                    lng = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if add != "":
            if " " in zc:
                country = "CA"
            else:
                country = "US"
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
