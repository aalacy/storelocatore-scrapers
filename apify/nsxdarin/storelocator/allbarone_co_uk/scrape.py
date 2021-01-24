import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("allbarone_co_uk")


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
    url = "https://www.allbarone.co.uk/sitemap.xml"
    r = session.get(url, headers=headers)
    website = "allbarone.co.uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://www.allbarone.co.uk/national-search/" in line:
            lurl = line.split("<loc>")[1].split("<")[0]
            if lurl.count("/") == 5:
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
        hours = ""
        Closed = False
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "covid/closed" in line2:
                Closed = True
            if '"@type":"Restaurant"' in line2:
                name = line2.split('"name":"')[1].split('"')[0]
                add = line2.split('"streetAddress":"')[1].split('"')[0]
                city = line2.split('"addressLocality":"')[1].split('"')[0]
                try:
                    state = line2.split('"addressRegion":"')[1].split('"')[0]
                except:
                    state = "<MISSING>"
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                lat = line2.split('"latitude":')[1].split(",")[0]
                lng = line2.split('"longitude":')[1].split("}")[0]
            if 'of-week">' in line2:
                hrs = line2.split('of-week">')[1].split("<")[0]
            if 'escription">' in line2:
                hrs = hrs + ": " + line2.split('escription">')[1].split("<")[0]
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if 'lass="phone-number">' in line2:
                phone = line2.split('lass="phone-number">')[1].split("<")[0]
        if hours == "":
            hours = "<MISSING>"
        if Closed or "00" not in hours:
            hours = "Temporarily Closed"
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


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
