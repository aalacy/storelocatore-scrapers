import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("thedrybar_com")


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
    url = "https://www.thedrybar.com/locations/"
    r = session.get(url, headers=headers)
    website = "thedrybar.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<a class="locations__name" href="' in line:
            locs.append(
                line.split('<a class="locations__name" href="')[1].split('"')[0]
            )
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
        store = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "&id=" in line2:
                store = line2.split("&id=")[1].split("&")[0]
                zc = line2.split("&id=")[0].rsplit("+", 1)[1]
            if 'data-lat="' in line2:
                lat = line2.split('data-lat="')[1].split('"')[0]
                lng = line2.split('data-lng="')[1].split('"')[0]
            if '<h1 class="location__name">' in line2:
                name = line2.split('<h1 class="location__name">')[1].split("<")[0]
            if '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0].strip()
            if '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0].strip()
            if '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0].strip()
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if ":</span>" in line2 and "Closed" not in line2:
                if (
                    "a" in line2.replace("span", "")
                    or "u" in line2.replace("span", "")
                    or "i" in line2.replace("span", "")
                    or "e" in line2.replace("span", "")
                    or "o" in line2.replace("span", "")
                ):
                    hrs = (
                        line2.split("span>")[1].split("<")[0]
                        + ": "
                        + line2.split("span")[3].split(">")[1].split("<")[0]
                    )
                    if hours == "":
                        hours = hrs
                    else:
                        hours = hours + "; " + hrs
                    hours = hours.replace("&#8209;", "-").replace("::", ":")
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
