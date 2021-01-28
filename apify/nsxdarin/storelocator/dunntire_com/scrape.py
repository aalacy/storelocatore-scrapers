import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("dunntire_com")


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
    url = "https://www.dunntire.com/locations"
    r = session.get(url, headers=headers)
    website = "dunntire.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<a href="https://www.dunntire.com/locations/' in line:
            locs.append(line.split('href="')[1].split('"')[0])
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
            if '"name":"' in line2:
                store = line2.split('"@id":"')[1].split('"')[0]
                name = line2.split('"name":"')[1].split('"')[0]
                phone = line2.split('"telephone":"')[1].split('"')[0]
                add = line2.split('"streetAddress":"')[1].split('"')[0]
                state = line2.split('"addressRegion":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                city = line2.split('"addressLocality":"')[1].split('"')[0]
            if '<a href="//www.google.com/maps/search/' in line2:
                lat = line2.split("query=")[1].split(",")[0]
                lng = line2.split("query=")[1].split(",")[1].split("+")[0]
            if '"dayOfWeek","name":"' in line2:
                days = line2.split('"dayOfWeek","name":"')
                for day in days:
                    if '"opens":"' in day:
                        hrs = (
                            day.split('"')[0]
                            + ": "
                            + day.split('"opens":"')[1].split('"')[0]
                            + "-"
                            + day.split('"closes":"')[1].split('"')[0]
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
