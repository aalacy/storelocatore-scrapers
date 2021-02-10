import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("trotters_co_uk")


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
    url = "https://www.trotters.co.uk/pages/our-stores"
    r = session.get(url, headers=headers)
    website = "trotters.co.uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'Store"><img' in line:
            items = line.split('Store"><img')
            for item in items:
                if 'title="' in item:
                    locs.append(
                        "https://www.trotters.co.uk"
                        + item.split('href="')[1].split('"')[0]
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
        lat = "<MISSING>"
        lng = "<MISSING>"
        hours = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if '<h1 class="seo-heading">' in line2:
                name = line2.split('h1 class="seo-heading">')[1].split("<")[0]
            if "Address:</strong> <br>" in line2:
                addinfo = (
                    line2.split("Address:</strong> <br>")[1]
                    .split("</p>")[0]
                    .replace("<br>", "|")
                )
                add = addinfo.split("|")[0]
                city = addinfo.split("|")[1]
                state = "<MISSING>"
                zc = addinfo.split("|")[2]
            if '<a href="tel:' in line2:
                phone = (
                    line2.split('<a href="tel:')[1].split('"')[0].replace("%20", " ")
                )
            if "day</td>" in line2 and "Bank" not in line2:
                hrs = line2.split('">')[1].split("<")[0] + ": "
                g = next(lines)
                g = str(g.decode("utf-8"))
                g = g.replace('uqo3">', 'uqo3"><span>').replace(
                    "<span><span>", "<span>"
                )
                hrs = hrs + g.split("<span>")[1].split("<")[0]
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        if "trotters-concession-in-harrods" in loc:
            name = "HARRODS"
            add = "Fourth Floor, Harrods Department Store, 87-135 Brompton Road, Knightsbridge"
            city = "London"
            state = "<MISSING>"
            zc = "SW1X 7XL"
            phone = "<MISSING>"
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
