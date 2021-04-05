import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("bayclubs_com")


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
    url = "https://www.bayclubs.com/locations/"
    r = session.get(url, headers=headers)
    website = "bayclubs.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<button class="button" data-href="' in line:
            locs.append(
                "https://www.bayclubs.com/locations"
                + line.split('<button class="button" data-href="')[1].split('"')[0]
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
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        CS = False
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "OPENING SOON<" in line2:
                CS = True
            if "COMING SOON<" in line2:
                CS = True
            if name == "" and "<title>" in line2:
                name = line2.split("<title>")[1].split("<")[0]
                if "|" in name:
                    name = name.split("|")[0].strip()
            if add == "" and "</strong></p>" in line2 and CS is False:
                g = next(lines)
                h = next(lines)
                g = str(g.decode("utf-8"))
                h = str(h.decode("utf-8"))
                add = g.split(">")[1].split("<")[0]
                addinfo = h.split("<")[0].strip().replace("\t", "")
                city = addinfo.split(",")[0]
                state = addinfo.split(",")[1].strip().split(" ")[0]
                zc = addinfo.rsplit(" ", 1)[1]
            if '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
            if "center: {lat:" in line2:
                lat = line2.split("center: {lat:")[1].split(",")[0].strip()
                lng = line2.split("lng: ")[1].split("}")[0]
            if ": </strong>" in line2 and "am -" in line2:
                hrs = (
                    line2.split("<br")[0]
                    .split("<strong>")[1]
                    .replace("</strong>", "")
                    .replace("  ", " ")
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        if lat == "":
            lat = "<MISSING>"
            lng = "<MISSING>"
        if CS is True:
            hours = "Coming Soon"
        if add == "":
            add = "<INACCESSIBLE>"
        if city == "":
            city = "<INACCESSIBLE>"
        if state == "":
            state = "<INACCESSIBLE>"
        if zc == "":
            zc = "<INACCESSIBLE>"
        if "locations/marin" in loc:
            add = "220 Corte Madera Town Center"
            city = "Corte Madera"
            state = "CA"
            zc = "94925"
        if "locations/financialdistrict" in loc:
            add = "555 California Street"
            city = "San Francisco"
            state = "CA"
            zc = "94104"
        if "locations/southsanfrancisco" in loc:
            add = "501 Carter Street"
            city = "Daly City"
            state = "CA"
            zc = "94014"
        if "locations/broadwaytennis" in loc:
            add = "60 Edwards Court"
            city = "Burlingame"
            state = "CA"
            zc = "94010"
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
