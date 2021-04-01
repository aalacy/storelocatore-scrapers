import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("stjosephhealth_org")


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
    website = "stjosephhealth.org"
    country = "US"
    typ = "<MISSING>"
    store = "<MISSING>"
    for x in range(1, 151):
        logger.info("Page " + str(x))
        url = (
            "https://www.providence.org/locations?postal=90009&lookup=&lookupvalue=&page="
            + str(x)
            + "&radius=5000&term="
        )
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '<div class="subhead-h3"><a href="' in line:
                stub = line.split('<div class="subhead-h3"><a href="')[1].split('"')[0]
                if "http" not in stub:
                    lurl = "https://www.providence.org" + stub
                    if lurl not in locs:
                        locs.append(lurl)
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
        hours = ""
        hours2 = ""
        hours3 = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "<b>Clinic Hours:<br /></b>" in line2 and hours3 == "":
                g = next(lines)
                g = str(g.decode("utf-8"))
                if "p.m.<" in g:
                    hours3 = (
                        g.split("</p></div>")[0]
                        .replace("<strong>", "")
                        .replace("</strong>", "")
                    )
            if '"telephone":"' in line2:
                phone = line2.split('"telephone":"')[1].split('"')[0]
            if '<div class="hours-text text-muted">' in line2 and hours2 == "":
                hours2 = line2.split('<div class="hours-text text-muted">')[1].split(
                    "</div"
                )[0]
                hours2 = hours2.replace("<p>", "").replace("</p>", "")
            if '"name":"' in line2:
                name = line2.split('"name":"')[1].split('"')[0]
                try:
                    hours = line2.split(',"openingHours":"')[1].split('"')[0]
                except:
                    hours = "<MISSING>"
                try:
                    add = line2.split('"streetAddress":"')[1].split('"')[0]
                except:
                    add = "<MISSING>"
                try:
                    state = line2.split('"addressRegion":"')[1].split('"')[0]
                except:
                    state = "<MISSING>"
                try:
                    zc = line2.split('"postalCode":"')[1].split('"')[0]
                except:
                    zc = "<MISSING>"
                try:
                    city = line2.split('"addressLocality":"')[1].split('"')[0]
                except:
                    city = "<MISSING>"
                try:
                    phone = line2.split('"telephone":"')[1].split('"')[0]
                except:
                    phone = "<MISSING>"
                try:
                    lat = line2.split('"latitude":')[1].split(",")[0]
                except:
                    lat = "<MISSING>"
                try:
                    lng = line2.split('"longitude":')[1].split("}")[0]
                except:
                    lng = "<MISSING>"
                try:
                    typ = line2.split('"@type":"')[1].split('"')[0]
                except:
                    typ = "<MISSING>"
        if typ != "<MISSING>" and name != "":
            if add == "":
                add = "<MISSING>"
            if city == "":
                city = "<MISSING>"
            if zc == "":
                zc = "<MISSING>"
            if phone == "":
                phone = "<MISSING>"
            if hours == "":
                hours = "<MISSING>"
            if state == "":
                state = "<MISSING>"
            name = name.replace("\\u0027", "'")
            add = add.replace("\\u0027", "'")
            if hours2 != "":
                hours = hours2
            if "p.m." in hours3:
                hours = hours3
            if "locations/providence-medical-associates" in loc:
                hours = "Mon - Fri: 8 a.m. - 5 p.m."
            if hours.strip() == "&nbsp;":
                hours = "<MISSING>"
            if "<!--" in hours:
                hours = "<MISSING>"
            if "<h4>Family" in hours or "<b>Clinic" in hours:
                hours = "<MISSING>"
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
