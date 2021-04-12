import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("biolifeplasma_com")


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
    url = "https://www.biolifeplasma.com/sitemap.xml"
    r = session.get(url, headers=headers)
    website = "biolifeplasma.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://www.biolifeplasma.com/locations/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
    for loc in locs:
        logger.info(loc)
        st = (
            loc.split("https://www.biolifeplasma.com/locations/")[1]
            .split("/")[0]
            .replace("%20", "+")
        )
        ct = loc.rsplit("/", 1)[1].replace("%20", "+")
        lurl = (
            "https://api-scheduler.biolifeplasma.com/centers/details?name="
            + ct
            + "&state="
            + st
        )
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
        r2 = session.get(lurl, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '{"id":' in line2:
                store = line2.split('{"id":')[1].split(",")[0]
                name = line2.split('"name":"')[1].split('"')[0]
                add = line2.split('"addressLine1":"')[1].split('"')[0]
                phone = line2.split('"telephone":"')[1].split('"')[0]
                lat = line2.split('"latitude":')[1].split(",")[0]
                lng = line2.split('"longitude":')[1].split(",")[0]
                state = line2.split('"stateCode":"')[1].split('"')[0]
                zc = line2.split('"zipcode":"')[1].split('"')[0]
                city = line2.split('"city":"')[1].split('"')[0]
                days = line2.split('"weekDayName":"')
                for day in days:
                    if '"weekDayIndex":' in day:
                        if 'isClosed":true' in day:
                            hrs = day.split('"')[0] + ": Closed"
                        else:
                            hrs = (
                                day.split('"')[0]
                                + ": "
                                + day.split(',"openingTime":"')[1].split(':00"')[0]
                                + "-"
                                + day.split('"closingTime":"')[1].split(':00"')[0]
                            )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
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
