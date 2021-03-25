import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("bjc_org")


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
    url = "https://www.bjc.org/About-Us/Locations"
    r = session.get(url, headers=headers)
    website = "bjc.org"
    country = "US"
    ltyp = "Hospital"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'class="tab-pane " id="' in line:
            ltyp = (
                line.split('class="tab-pane " id="')[1]
                .split('"')[0]
                .replace("-", " ")
                .title()
            )
        if "more information" in line.lower():
            locs.append(line.split('href="')[1].split('"')[0] + "|" + ltyp)
    for loc in locs:
        lurl = loc.split("|")[0]
        logger.info(lurl)
        typ = loc.split("|")[1]
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
        hours2 = ""
        r2 = session.get(lurl, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "<h1>" in line2:
                name = line2.split("<h1>")[1].split("<")[0]
            if 'lass="address">' in line2:
                next(lines)
                g = next(lines)
                h = next(lines)
                g = str(g.decode("utf-8"))
                h = str(h.decode("utf-8"))
                add = g.split("<")[0].strip().replace("\t", "")
                addinfo = (
                    h.strip().replace("\t", "").replace("\r", "").replace("\n", "")
                )
                try:
                    city = addinfo.split(",")[0]
                    state = addinfo.split(",")[1].rsplit(" ", 1)[0]
                    zc = addinfo.rsplit(" ", 1)[1]
                except:
                    city = ""
                    state = ""
                    zc = ""
            if "<a href=tel:" in line2:
                phone = line2.split("<a href=tel:")[1].split(">")[1].split("<")[0]
            if '"closes": "' in line2:
                hc = line2.split('"closes": "')[1].split('"')[0]
            if '"dayOfWeek": "http://schema.org/' in line2:
                day = line2.split('"dayOfWeek": "http://schema.org/')[1].split('"')[0]
            if '"opens": "' in line2:
                ho = line2.split('"opens": "')[1].split('"')[0]
                hrs = day + ": " + ho + "-" + hc
                hrs = hrs.replace("00:00:00-00:00:00", "Closed")
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if "Operating Hours:</strong><br><strong>" in line2:
                hours2 = line2.split("Operating Hours:</strong><br><strong>")[1].split(
                    "</p><"
                )[0]
        if hours == "":
            hours = "<MISSING>"
        if hours2 != "":
            hours = hours2
        hours = hours.replace("</strong>", "")
        hours = hours.replace("</strong><br><strong>", "; ")
        hours = hours.replace(":00;", ";").replace(":00-", "-")
        city = city.replace("&#39;", "'")
        add = add.replace("&#39;", "'")
        name = name.replace("&#39;", "'")
        city = city.replace("&amp;", "&")
        add = add.replace("&amp;", "&")
        name = name.replace("&amp;", "&")
        hours = hours.replace("<br><strong>", "; ")
        if phone == "":
            phone = "<MISSING>"
        if city != "":
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
