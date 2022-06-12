import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("casinoeurope_com__uk")


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
                "raw_address",
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
    states = []
    url = "https://www.casinoseurope.com/uk/all-casinos/"
    r = session.get(url, headers=headers)
    website = "casinoeurope.com/uk"
    typ = "<MISSING>"
    country = "GB"
    Found = False
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "All UK Casinos</h1>" in line:
            Found = True
        if Found and '<div class="' in line:
            Found = False
        if Found and '<li><a href="/uk/' in line:
            lurl = (
                "https://www.casinoseurope.com" + line.split('href="')[1].split('"')[0]
            )
            if "(" not in lurl:
                states.append(lurl)
            else:
                if lurl not in locs:
                    locs.append(lurl)
    for state in states:
        logger.info(state)
        CFound = False
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<h1 class="entry-title">' in line2:
                CFound = True
            if CFound and "</ul>" in line2:
                CFound = False
            if CFound and '<li><a href="/uk/' in line2:
                purl = (
                    "https://www.casinoseurope.com"
                    + line2.split('href="')[1].split('"')[0]
                )
                if purl not in locs:
                    locs.append(purl)
    for loc in locs:
        logger.info(loc)
        name = ""
        add = "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        zc = "<MISSING>"
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = "<MISSING>"
        rawadd = ""
        AFound = False
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<h1 class="entry-title">' in line2:
                name = line2.split('<h1 class="entry-title">')[1].split("<")[0]
            if '"latitude":"' in line2:
                lat = line2.split('"latitude":"')[1].split('"')[0]
                lng = line2.split('"longitude":"')[1].split('"')[0]
            if "Phone: " in line2:
                phone = line2.split("Phone:")[1].split("<")[0].strip()
            if "<h3>Contact Details" in line2:
                AFound = True
            if AFound and "Phone" in line2:
                AFound = False
            if (
                AFound
                and "<p>" not in line2
                and "<h3>" not in line2
                and "<br />" in line2
            ):
                if rawadd == "":
                    rawadd = line2.split("<")[0]
                else:
                    rawadd = rawadd + " " + line2.split("<")[0]
                addr = parse_address_intl(rawadd)
                city = addr.city
                zc = addr.postcode
                add = addr.street_address_1
                state = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if lat == "":
            lat = "<MISSING>"
            lng = "<MISSING>"
        if name != "" and rawadd != "":
            yield [
                website,
                loc,
                name,
                rawadd,
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
