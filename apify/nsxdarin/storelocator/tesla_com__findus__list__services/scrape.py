import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("tesla_com__findus__list__services")


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
    session = SgRequests()
    url = "https://www.tesla.com/findus/list/services"
    r = session.get(url, headers=headers)
    website = "tesla.com/findus/list/services"
    typ = "<MISSING>"
    country = ""
    logger.info("Pulling Stores")
    Found = False
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<a href="/findus/location/service/' in line:
            locs.append("https://www.tesla.com" + line.split('href="')[1].split('"')[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        typ = ""
        state = ""
        zc = ""
        CS = False
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        HFound = True
        hours = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if '<span class="coming-soon">Coming Soon</span>' in line2:
                CS = True
            if "<title>" in line2:
                name = line2.split("<title>")[1].split(" |")[0]
            if '<span class="street-address">' in line2:
                rawadd = line2.split('<span class="street-address">')[1].split("<")[0]
            if '<span class="extended-address">' in line2:
                rawadd = (
                    rawadd
                    + " "
                    + line2.split('<span class="extended-address">')[1].split("<")[0]
                )
                rawadd = add.strip()
            if '<span class="locality">' in line2:
                g = line2.replace("  ", " ").replace("  ", " ")
                rawadd = rawadd + " " + g.split('ity">')[1].split("<")[0]
                if "<br />" in g:
                    rawadd = rawadd + " " + g.split("<br />")[1].split("<")[0]
                addr = parse_address_intl(rawadd)
                city = addr.city
                zc = addr.postcode
                state = addr.state
                add = addr.street_address_1
                if add is None:
                    add = "<MISSING>"
                else:
                    add = add.strip()
            if '<span class="type">' in line2 and typ == "":
                typ = typ + "; " + line2.split('<span class="type">')[1].split("<")[0]
                if phone == "":
                    phone = line2.split('<span class="value">')[1].split("<")[0]
            if '<a href="https://maps.google.com/maps?daddr=' in line2:
                lat = line2.split('<a href="https://maps.google.com/maps?daddr=')[
                    1
                ].split(",")[0]
                lng = (
                    line2.split('<a href="https://maps.google.com/maps?daddr=')[1]
                    .split(",")[1]
                    .split('"')[0]
                )
            if "Hours</strong><br />" in line2 and "day" in line2 and HFound:
                hours = (
                    line2.split("Hours</strong><br />")[1]
                    .replace("<br />", "; ")
                    .replace("<br/>", "; ")
                    .replace("\r", "")
                    .replace("\t", "")
                    .replace("\n", "")
                    .strip()
                )
                HFound = False
            if "Hours</strong><br/>" in line2 and "day" in line2 and HFound:
                hours = (
                    line2.split("Hours</strong><br/>")[1]
                    .replace("<br/>", "; ")
                    .replace("<br />", "; ")
                    .replace("\r", "")
                    .replace("\t", "")
                    .replace("\n", "")
                    .strip()
                )
                HFound = False
            if "Hours</strong><br />" in line2 and "day" not in line2 and HFound:
                g = next(lines)
                g = str(g.decode("utf-8"))
                if "day" not in g:
                    g = next(lines)
                    g = str(g.decode("utf-8"))
                while "day" in g:
                    if hours == "":
                        hours = (
                            g.replace("<br />", "; ")
                            .replace("<br/>", "; ")
                            .replace("\r", "")
                            .replace("\t", "")
                            .replace("\n", "")
                            .strip()
                        )
                    else:
                        hours = (
                            hours
                            + "; "
                            + g.replace("<br />", "; ")
                            .replace("<br/>", "; ")
                            .replace("<br/>", "; ")
                            .replace("\r", "")
                            .replace("\t", "")
                            .replace("\n", "")
                            .strip()
                        )
                    g = next(lines)
                    g = str(g.decode("utf-8"))
                HFound = False
            if "Hours</strong><br/>" in line2 and "day" not in line2 and HFound:
                g = next(lines)
                g = str(g.decode("utf-8"))
                if "day" not in g:
                    g = next(lines)
                    g = str(g.decode("utf-8"))
                while "day" in g:
                    if hours == "":
                        hours = (
                            g.replace("<br />", "; ")
                            .replace("<br/>", "; ")
                            .replace("\r", "")
                            .replace("\t", "")
                            .replace("\n", "")
                            .strip()
                        )
                    else:
                        hours = (
                            hours
                            + "; "
                            + g.replace("<br />", "; ")
                            .replace("<br/>", "; ")
                            .replace("<br/>", "; ")
                            .replace("\r", "")
                            .replace("\t", "")
                            .replace("\n", "")
                            .strip()
                        )
                    g = next(lines)
                    g = str(g.decode("utf-8"))
                HFound = False
        if "; <p>" in hours:
            hours = hours.split("; <p>")[0]
        if hours == "":
            hours = "<MISSING>"
        hours = hours.replace(";;", ";")
        if lat == "":
            lat = "<MISSING>"
            lng = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if "</p>" in hours:
            hours = hours.split("</p>")[0].strip()
        typ = typ.replace("; ", "")
        if typ == "":
            typ = "Store"
        if CS:
            name = name + " - Coming Soon"
        if state == "":
            state = "<MISSING>"
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
