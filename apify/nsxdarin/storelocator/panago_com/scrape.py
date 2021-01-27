import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("rubios_com")


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
    url = "https://www.panago.com/location-sitemap.xml"
    r = session.get(url, headers=headers)
    website = "panago.com"
    typ = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://www.panago.com/location/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        country = "CA"
        phone = ""
        lat = ""
        lng = ""
        store = "<MISSING>"
        hours = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                name = line2.split("<title>")[1].split(" |")[0]
            if '<span class="street">' in line2:
                add = line2.split('<span class="street">')[1].split("<")[0]
            if '<span class="city">' in line2:
                city = line2.split('<span class="city">')[1].split("<")[0]
            if '<span class="province">' in line2:
                state = line2.split('<span class="province">')[1].split("<")[0]
            if '<span class="postal">' in line2:
                zc = line2.split('<span class="postal">')[1].split("<")[0]
            if '<div class="phone">' in line2:
                phone = line2.split('<div class="phone">')[1].split("<")[0]
            if "<label>" in line2:
                day = line2.split("<label>")[1].split("<")[0]
            if "m</span>" in line2 and ":" in line2:
                hrs = day + ": " + line2.split("<span>")[1].split("<")[0]
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if 'data-store-id="' in line2:
                store = line2.split('data-store-id="')[1].split('"')[0]
            if '"latitude":"' in line2:
                lat = line2.split('"latitude":"')[1].split('"')[0]
                lng = line2.split('"longitude":"')[1].split('"')[0]
        if phone == "":
            phone = "<MISSING>"
        if hours == "":
            hours = "Sun-Sat: Closed"
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
