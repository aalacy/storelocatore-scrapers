import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("butlerhealthsystem_org")


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
    url = "https://www.butlerhealthsystem.org/Locations.aspx"
    r = session.get(url, headers=headers)
    website = "butlerhealthsystem.org"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'ata-longitude="' in line:
            llng = line.split('ata-longitude="')[1].split('"')[0]
            llat = line.split('ata-latitude="')[1].split('"')[0]
        if 'class="btn v1">View Details</a>' in line:
            locs.append(
                "https://www.butlerhealthsystem.org/"
                + line.split('href="')[1].split('"')[0]
                + "|"
                + llat
                + "|"
                + llng
            )
    for loc in locs:
        lurl = loc.split("|")[0]
        logger.info(lurl)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = loc.split("|")[1]
        lng = loc.split("|")[2]
        hours = ""
        HFound = False
        r2 = session.get(lurl, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "<h3>Hours" in line2:
                HFound = True
            if HFound and "</div>" in line2:
                HFound = False
            if HFound and "&ndash;" in line2:
                hrs = (
                    line2.strip()
                    .replace("<br>", "")
                    .replace("\n", "")
                    .replace("\r", "")
                    .replace("\t", "")
                    .replace("&ndash;", "-")
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if "<h1><span>" in line2:
                name = line2.split("<h1><span>")[1].split("<")[0]
            if add == "" and '<span itemprop="streetAddress">' in line2:
                add = (
                    line2.split('<span itemprop="streetAddress">')[1]
                    .replace("\t", "")
                    .replace("\r", "")
                    .replace("\n", "")
                    .strip()
                )
                g = next(lines)
                g = next(lines)
                g = str(g.decode("utf-8"))
                if "<br>" in g:
                    add = (
                        add
                        + " "
                        + g.split("<br>")[1]
                        .replace("\t", "")
                        .replace("\r", "")
                        .replace("\n", "")
                        .strip()
                    )
            if 'state: "' in line2:
                state = line2.split('state: "')[1].split('"')[0]
            if 'city: "' in line2:
                city = line2.split('city: "')[1].split('"')[0]
            if 'zipcode: "' in line2:
                zc = line2.split('zipcode: "')[1].split('"')[0]
            if phone == "" and 'itemprop="telephone">' in line2:
                phone = (
                    line2.split('itemprop="telephone">')[1]
                    .split("<")[0]
                    .replace(".", "-")
                )
        if hours == "":
            hours = "<MISSING>"
        hours = (
            hours.replace("<p>", "")
            .replace("</p>", "")
            .replace("<span>", "")
            .replace("</span>", "")
            .strip()
        )
        add = add.replace("Rose E. Schneider Family YMCA<br>", "")
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
