import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("tesla_com")


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
    url = "https://www.tesla.com/findus/list/stores/United+Kingdom"
    r = session.get(url, headers=headers)
    website = "tesla.com"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<a href="/findus/location/' in line:
            locs.append("https://www.tesla.com" + line.split('href="')[1].split('"')[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = "<MISSING>"
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                name = line2.split("<title>")[1].split(" |")[0]
            if '<span class="street-address">' in line2:
                add = line2.split('<span class="street-address">')[1].split("<")[0]
            if '<span class="extended-address">' in line2:
                add = (
                    add
                    + " "
                    + line2.split('<span class="extended-address">')[1].split("<")[0]
                )
                add = add.strip()
            if '<span class="locality">' in line2:
                addinfo = line2.split('<span class="locality">')[1].split("<")[0]
                if addinfo.count(" ") == 2:
                    city = addinfo.split(" ")[2]
                    zc = addinfo.split(" ")[0] + " " + addinfo.split(" ")[1]
                else:
                    city = addinfo.split(" ")[2] + " " + addinfo.split(" ")[3]
                    zc = addinfo.split(" ")[0] + " " + addinfo.split(" ")[1]
            if '<span class="type">' in line2:
                typ = line2.split('<span class="type">')[1].split("<")[0]
                phone = line2.split('<span class="value">')[1].split("<")[0].strip()
            if '<a href="https://maps.google.com/maps?daddr=' in line2:
                lat = line2.split('<a href="https://maps.google.com/maps?daddr=')[
                    1
                ].split(",")[0]
                lng = (
                    line2.split('<a href="https://maps.google.com/maps?daddr=')[1]
                    .split(",")[1]
                    .split('"')[0]
                )
            if "Hours</strong><br />" in line2:
                hours = (
                    line2.split("Hours</strong><br />")[1]
                    .replace("<br />", "; ")
                    .replace("<br/>", "; ")
                    .replace("\r", "")
                    .replace("\t", "")
                    .replace("\n", "")
                    .strip()
                )
            if "Hours</strong><br/>" in line2:
                hours = (
                    line2.split("Hours</strong><br/>")[1]
                    .replace("<br/>", "; ")
                    .replace("<br />", "; ")
                    .replace("\r", "")
                    .replace("\t", "")
                    .replace("\n", "")
                    .strip()
                )
            if "Sales Hours</strong><br/>" in line2:
                g = next(lines)
                g = str(g.decode("utf-8"))
                if "day" in g:
                    hours = (
                        g.replace("\r", "")
                        .replace("\n", "")
                        .replace("\t", "")
                        .strip()
                        .replace("<br/>", "; ")
                        .replace("<br>", "; ")
                        .replace("<br />", "; ")
                    )
        if "; <p>" in hours:
            hours = hours.split("; <p>")[0]
        if hours == "":
            hours = "<MISSING>"
        if lat == "":
            lat = "<MISSING>"
            lng = "<MISSING>"
        if add == "":
            add = "<MISSING>"
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
    locs = []
    url = "https://www.tesla.com/findus/list/stores/United+States"
    r = session.get(url, headers=headers)
    website = "tesla.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<a href="/findus/location/' in line:
            locs.append("https://www.tesla.com" + line.split('href="')[1].split('"')[0])
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
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                name = line2.split("<title>")[1].split(" |")[0]
            if '<span class="street-address">' in line2:
                add = line2.split('<span class="street-address">')[1].split("<")[0]
            if '<span class="extended-address">' in line2:
                add = (
                    add
                    + " "
                    + line2.split('<span class="extended-address">')[1].split("<")[0]
                )
                add = add.strip()
            if '<span class="locality">' in line2:
                city = line2.split('<span class="locality">')[1].split(",")[0]
                state = line2.split(", ")[1].split(" ")[0]
                zc = line2.split("</span>")[0].rsplit(" ", 1)[1]
            if '<span class="type">' in line2:
                typ = line2.split('<span class="type">')[1].split("<")[0]
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
            if "Store Hours</strong><br />" in line2:
                hours = (
                    line2.split("Store Hours</strong><br />")[1]
                    .split("</p>")[0]
                    .replace("<br />", "; ")
                    .replace("<br/>", "; ")
                )
            if "Store Hours</strong><br/>" in line2:
                hours = (
                    line2.split("Store Hours</strong><br/>")[1]
                    .split("</p>")[0]
                    .replace("<br/>", "; ")
                    .replace("<br />", "; ")
                )
        if "; <p>" in hours:
            hours = hours.split("; <p>")[0]
        if hours == "":
            hours = "<MISSING>"
        if lat == "":
            lat = "<MISSING>"
            lng = "<MISSING>"
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
    locs = []
    url = "https://www.tesla.com/findus/list/stores/Canada"
    r = session.get(url, headers=headers)
    website = "tesla.com"
    typ = "<MISSING>"
    country = "CA"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<a href="/findus/location/' in line:
            locs.append("https://www.tesla.com" + line.split('href="')[1].split('"')[0])
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
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                name = line2.split("<title>")[1].split(" |")[0]
            if '<span class="street-address">' in line2:
                add = line2.split('<span class="street-address">')[1].split("<")[0]
            if '<span class="extended-address">' in line2:
                add = (
                    add
                    + " "
                    + line2.split('<span class="extended-address">')[1].split("<")[0]
                )
                add = add.strip()
            if '<span class="locality">' in line2:
                g = line2.replace("  ", " ").replace("  ", " ")
                city = g.split('<span class="locality">')[1].split(",")[0]
                state = g.split(", ")[1].split(" ")[0]
                zc = (
                    g.split('<span class="locality">')[1]
                    .split("<")[0]
                    .split(",")[1]
                    .strip()
                    .split(" ", 1)[1]
                )
            if '<span class="type">' in line2:
                typ = line2.split('<span class="type">')[1].split("<")[0]
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
            if "Store Hours</strong><br />" in line2:
                hours = (
                    line2.split("Store Hours</strong><br />")[1]
                    .split("</p>")[0]
                    .replace("<br />", "; ")
                    .replace("<br/>", "; ")
                )
            if "Store Hours</strong><br/>" in line2:
                hours = (
                    line2.split("Store Hours</strong><br/>")[1]
                    .split("</p>")[0]
                    .replace("<br/>", "; ")
                    .replace("<br />", "; ")
                )
        if "; <p>" in hours:
            hours = hours.split("; <p>")[0]
        if hours == "":
            hours = "<MISSING>"
        if lat == "":
            lat = "<MISSING>"
            lng = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if "parkroyalvancouver" in loc:
            state = "BC"
            zc = "V7T 2Z3"
        if "robsonstreet" in loc:
            state = "BC"
            zc = "V6Z 2V7"
        if "torontosherwaygardens" in loc:
            state = "ON"
            zc = "M9C 1B8"
        if "torontovaughan" in loc:
            state = "ON"
            zc = "L4L 8V1"
        if "yorkdale" in loc:
            state = "ON"
            zc = "M6A 2T9"
        if "https://www.tesla.com/findus/location/store/montrealferrier" in loc:
            hours = "M-F: 7:30-17:30; Sat-Sun: Closed"
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
