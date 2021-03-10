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
    url = "https://www.rubios.com/sitemap.xml"
    r = session.get(url, headers=headers)
    website = "rubios.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://www.rubios.com/restaurant-locations" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        phone = ""
        lat = ""
        lng = ""
        store = "<MISSING>"
        hours = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if '<meta property="og:title" content="' in line2:
                name = line2.split('<meta property="og:title" content="')[1].split('"')[
                    0
                ]
            if 'store-address__address">' in line2:
                g = next(lines)
                h = next(lines)
                g = str(g.decode("utf-8"))
                h = str(h.decode("utf-8"))
                add = (
                    g.split('"field-content">')[1].split("<")[0]
                    + " "
                    + g.split('"field-content">')[2].split("<")[0]
                )
                add = add.strip()
                if 'store-address__address_2">' not in h:
                    city = g.split('"field-content">')[3].split("<")[0]
                    state = h.split('"field-content">')[1].split("<")[0]
                    zc = h.split('"field-content">')[2].split("<")[0]
                else:
                    g = next(lines)
                    h = next(lines)
                    g = str(g.decode("utf-8"))
                    h = str(h.decode("utf-8"))
                    city = g.split('"field-content">')[1].split("<")[0]
                    state = h.split('"field-content">')[1].split("<")[0]
                    zc = h.split('<span class="field-content">')[2].split("<")[0]
            if '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
            if '"lat":"' in line2:
                lat = line2.split('"lat":"')[1].split('"')[0]
                lng = line2.split('"lng":"')[1].split('"')[0]
            if 'style="width: 6.6em;">' in line2:
                days = line2.split('style="width: 6.6em;">')
                for day in days:
                    if '<div class="field-content">' not in day:
                        hrs = (
                            day.split("<")[0].strip()
                            + ": "
                            + day.split("oh-display-hours")[1]
                            .split(">")[1]
                            .split("<")[0]
                            .strip()
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
