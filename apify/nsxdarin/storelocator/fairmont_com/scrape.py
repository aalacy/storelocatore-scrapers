import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("fairmont_com")


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
    url = "https://www.fairmont.com"
    r = session.get(url, headers=headers)
    website = "fairmont.com"
    typ = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'United States</p><ul class="property-list">' in line:
            uslist = (
                line.split('United States</p><ul class="property-list">')[1]
                .split('<div class="property-list-holder"')[0]
                .split('<a href = "')
            )
            for item in uslist:
                if "</a></li>" in item:
                    locs.append("https://www.fairmont.com" + item.split('"')[0] + "|US")
            calist = (
                line.split('Canada</p><ul class="property-list">')[1]
                .split('<div class="property-list-holder"')[0]
                .split('<a href = "')
            )
            for item in calist:
                if "</a></li>" in item:
                    locs.append("https://www.fairmont.com" + item.split('"')[0] + "|CA")
            uklist = (
                line.split('>United Kingdom</p><ul class="property-list">')[1]
                .split('d="Middle_East_and_A')[0]
                .split('<a href = "')
            )
            for item in uklist:
                if "</a></li>" in item:
                    locs.append("https://www.fairmont.com" + item.split('"')[0] + "|GB")
    for loc in locs:
        purl = loc.split("|")[0]
        country = loc.split("|")[1]
        logger.info(purl)
        name = ""
        add = ""
        city = ""
        if country == "GB":
            state = "<MISSING>"
        zc = ""
        store = ""
        phone = ""
        lat = ""
        lng = ""
        hours = "<MISSING>"
        r2 = session.get(purl, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "'hotelname' : '" in line2:
                name = line2.split("'hotelname' : '")[1].split("'")[0]
            if "'hotelcode' : '" in line2:
                store = line2.split("'hotelcode' : '")[1].split("'")[0]
            if '<ul class="hotels-common-details">' in line2:
                next(lines)
                next(lines)
                g = next(lines)
                g = str(g.decode("utf-8"))
                if "<li>" in g:
                    g = next(lines)
                    g = str(g.decode("utf-8"))
                g = g.replace("\r", "").replace("\t", "").replace("\n", "").strip()
                g = g.replace("Boston,Mass", "Boston - Mass")
                g = g.replace("Stars, Cal", "Stars, Los Angeles - Cal")
                g = g.replace("181,", "181")
                g = g.replace("Strand, London", "Strand, London - London")
                g = g.replace("Scotland", "Scotland - Scotland")
                add = g.split(",")[0]
                city = g.split(",")[1].strip().split(" - ")[0]
                state = g.split(",")[1].strip().split(" - ")[1]
                if "United States" in g:
                    zc = g.rsplit(" ", 1)[1]
                if "Canada" in g:
                    zc = g.split("Canada ")[1].strip()
                if "United Kingdom" in g:
                    zc = g.split("United Kingdom")[1].strip()
            if 'aria-label="Phone number"' in line2:
                phone = (
                    line2.split('aria-label="Phone number"')[1]
                    .split(">")[1]
                    .split("<")[0]
                )
            if 'Latitude" value="' in line2:
                lat = line2.split('Latitude" value="')[1].split('"')[0]
            if 'Longitude" value="' in line2:
                lng = line2.split('Longitude" value="')[1].split('"')[0]
        if " Est" in zc:
            zc = zc.split(" Est")[0].strip()
        if "900 Canada Place" in add:
            zc = "V6C 3L5"
        if "900 West Georgia Street" in add:
            zc = "V6C 2W6"
        if "1038 Canada Place" in add:
            zc = "V6C 0B9"
        yield [
            website,
            purl,
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
