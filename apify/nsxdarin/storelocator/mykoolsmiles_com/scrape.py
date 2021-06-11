import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("mykoolsmiles_com")


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
    url = "https://www.mykoolsmiles.com/locations-sitemap.xml"
    r = session.get(url, headers=headers)
    website = "mykoolsmiles.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://www.mykoolsmiles.com/locations/" in line:
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
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '{"@context":"https://schema.org"' in line2:
                name = line2.rsplit('"name":"', 1)[1].split('"')[0]
            if add == "" and 'Maps" target="_blank">' in line2:
                addinfo = line2.split('Maps" target="_blank">')[1].split("<")[0]
                addinfo = addinfo.replace(", USA", "").strip()
                add = addinfo.split(",")[0]
                city = addinfo.split(",")[1].strip()
                state = addinfo.split(",")[2].strip().split(" ")[0]
                zc = addinfo.rsplit(" ", 1)[1]
            if '<p class="' in line2 and "day:" in line2:
                hrs = line2.split(">")[1].split("<")[0]
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
            if lat == "" and "api=1&destination=" in line2:
                lat = line2.split("api=1&destination=")[1].split(",")[0]
                lng = line2.split("api=1&destination=")[1].split(",")[1].split('"')[0]
        name = name.replace("&#8211;", "-")
        hours = (
            hours.replace(" (Alt weeks 9:00AM - 6:00PM)", "")
            .replace("  VARIES ", "")
            .replace("  (Alt weeks 8:00AM - 5:00PM)", "")
            .replace("  (Alt weeks 8:00AM - 5:00PM)", "")
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
