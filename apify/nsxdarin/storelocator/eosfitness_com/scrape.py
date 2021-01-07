import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("eosfitness_com")


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
    url = "https://eosfitness.com/find-club/"
    r = session.get(url, headers=headers)
    website = "eosfitness.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'data-id="' in line:
            sid = line.split('data-id="')[1].split('"')[0]
        if 'data-lat="' in line:
            lat = line.split('data-lat="')[1].split('"')[0]
        if 'data-lon="' in line:
            lng = line.split('lon="')[1].split('"')[0]
        if '">Go to Gym Page</a>' in line:
            locs.append(
                line.split('href="')[1].split('"')[0]
                + "|"
                + sid
                + "|"
                + lat
                + "|"
                + lng
            )
    for loc in locs:
        lurl = loc.split("|")[0]
        store = loc.split("|")[1]
        lat = loc.split("|")[2]
        lng = loc.split("|")[3]
        logger.info(lurl)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        phone = ""
        hours = ""
        r2 = session.get(lurl, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '"alternateName":"' in line2:
                name = (
                    line2.split('"alternateName":"')[1]
                    .split('"')[0]
                    .replace("\\u014d", "o")
                    .replace("\\", "")
                )
            if '"streetAddress":"' in line2:
                add = line2.split('"streetAddress":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                state = line2.split('"addressRegion":"')[1].split('"')[0]
                city = line2.split('"addressLocality":"')[1].split('"')[0]
            if 'club-info__info club-info__info--phone">' in line2:
                if '<a href="tel:' not in line2:
                    phone = (
                        line2.split('club-info__info club-info__info--phone">')[1]
                        .split("<")[0]
                        .strip()
                    )
                else:
                    phone = (
                        line2.split('<a href="tel:')[1].split('"')[0].replace("+1", "")
                    )
        hours = "Sun-Sat: 24 Hours"
        name = name.replace("&#8211;", "-")
        if add != "":
            yield [
                website,
                lurl,
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
