import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("accuquest_net")


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
    url = "https://accuquest.com/store_page-sitemap.xml"
    r = session.get(url, headers=headers)
    website = "accuquest.net"
    typ = "<MISSING>"
    country = "US"
    store = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if (
            "<loc>https://accuquest.com/location-details/" in line
            and "/test-" not in line
        ):
            lurl = line.split("<loc>")[1].split("<")[0]
            if lurl != "https://accuquest.com/location-details/":
                locs.append(lurl)
    for loc in locs:
        logger.info(loc)
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        hours = ""
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if '<h1 class="entry-title" itemprop="headline">' in line2:
                name = line2.split('<h1 class="entry-title" itemprop="headline">')[
                    1
                ].split("<")[0]
            if "Address</strong><br />" in line2:
                g = next(lines)
                g = str(g.decode("utf-8"))
                add = g.split(",")[0]
                g = next(lines)
                g = str(g.decode("utf-8"))
                if "Bad Axe" in g:
                    city = "Bad Axe"
                    state = "Michigan"
                    zc = "48413"
                elif "Eau Claire W" in g:
                    city = "Eau Claire"
                    state = "Wisconsin"
                    zc = "54701"
                else:
                    city = g.split(",")[0]
                    state = g.split(",")[1].strip().rsplit(" ", 1)[0]
                    zc = g.split("<")[0].rsplit(" ", 1)[1]
            if "day-<" in line2:
                hrs = (
                    line2.split("<br>")[0]
                    .replace("</strong>", "")
                    .replace("<strong>", "")
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if "days-<" in line2:
                hrs = (
                    line2.split("<br>")[0]
                    .replace("</strong>", "")
                    .replace("<strong>", "")
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if "day</strong>" in line2:
                hrs = (
                    line2.split("<strong>")[1].split("<br>")[0].replace("</strong>", "")
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if "Call: (" in line2:
                phone = "(" + line2.split("Call: (")[1].split("<")[0].strip()
            if '<a href="https://www.google.com/maps/' in line2:
                lat = line2.split("/@")[1].split(",")[0]
                lng = line2.split("/@")[1].split(",")[1]
        hours = hours.replace("<p>", "")
        name = name.replace("&#8211;", "-")
        if hours == "":
            hours = "<MISSING>"
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
