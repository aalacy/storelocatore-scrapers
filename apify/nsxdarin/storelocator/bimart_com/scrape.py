import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("bimart_com")


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
    url = "https://www.bimart.com/retail-locations-archive/markers"
    r = session.get(url, headers=headers)
    website = "bimart.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    lines = r.iter_lines()
    for line in lines:
        line = str(line.decode("utf-8"))
        if '"coordinates":' in line:
            g = next(lines)
            g = str(g.decode("utf-8"))
            llng = g.split(",")[0].strip().replace("\t", "")[:10]
            g = next(lines)
            g = str(g.decode("utf-8"))
            llat = g.strip().replace("\r", "").replace("\n", "").replace("\t", "")[:10]
        if '"link": "' in line:
            lurl = "https://www.bimart.com" + line.split('"link": "')[1].split('"')[
                0
            ].replace("\\", "")
            locs.append(lurl + "|" + llat + "|" + llng)
    for loc in locs:
        logger.info(loc.split("|")[0])
        lurl = loc.split("|")[0]
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
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<h1 class="entry-title">' in line2:
                name = line2.split('<h1 class="entry-title">')[1].split("<")[0].strip()
            if '<p id="street">' in line2:
                addinfo = (
                    line2.split('<p id="street">')[1]
                    .split("<")[0]
                    .replace(", United States", "")
                )
                zc = "<MISSING>"
                add = addinfo.split(",")[0]
                city = addinfo.split(",")[1].strip()
                state = addinfo.split(",")[2].strip()
            if '<a class="phone-link" href="tel:' in line2 and phone == "":
                phone = line2.split('<a class="phone-link" href="tel:')[1].split('"')[0]
            if ">Store</strong>" in line2:
                HFound = True
            if HFound and '<p id="' in line2 and ">Store</strong>" not in line2:
                HFound = False
            if HFound and "day" in line2 and "href" not in line2:
                hrs = line2.split("<p>")[1].split("<")[0].strip()
            if HFound and "pm" in line2:
                hrs = hrs + ": " + line2.split("<p>")[1].split("<")[0].strip()
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        if "Rathdrum" in lurl:
            phone = phone[:12]
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
