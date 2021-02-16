import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("coxhealth_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


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
    url = "https://www.coxhealth.com/our-hospitals-and-clinics/our-locations/"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if "View Location Info</a>" in line:
            lurl = "https://www.coxhealth.com" + line.split('href="')[1].split('"')[0]
            locs.append(lurl)
    for loc in locs:
        logger.info(("Pulling Location %s..." % loc))
        website = "coxhealth.com"
        typ = "<MISSING>"
        hours = "<MISSING>"
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        lines = r2.iter_lines(decode_unicode=True)
        name = ""
        state = ""
        add = ""
        city = ""
        zc = ""
        country = "US"
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        for line2 in lines:
            if "open 24 hours" in line2.lower():
                hours = "Open 24 Hours"
            if "Hours</h3>" in line2:
                g = (
                    next(lines)
                    .replace("<span>", "")
                    .replace("</span>", "")
                    .replace("<br/>", "; ")
                )
                g = g.replace('<p style="text-align: left;">', "<p>").replace(
                    '</p><p style="text-align: left;">', "; "
                )
                if hours != "Open 24 Hours":
                    hours = g.split("<p>")[1].split("</p>")[0]
            if "<title>" in line2:
                name = line2.split("<title>")[1].split(" |")[0]
            if "Address</h3>" in line2:
                next(lines)
                next(lines)
                g = next(lines)
                csz = (
                    next(lines)
                    .replace("\r", "")
                    .replace("\t", "")
                    .replace("\n", "")
                    .strip()
                    .replace("  ", " ")
                )
                add = g.split("<")[0].strip().replace("\t", "")
                if "," in csz:
                    city = csz.split(",")[0]
                    state = csz.split(",")[1].strip().split(" ")[0]
                    zc = csz.rsplit(" ", 1)[1]
                else:
                    add = add + " " + csz
                    state = "MO"
                    city = "Springfield"
                    zc = "65807"
            if phone == "" and '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
            if 'btn-icon" href="tel:' in line2:
                phone = line2.split('btn-icon" href="tel:')[1].split('"')[0]
            if 'data-lat="' in line2:
                lat = line2.split('data-lat="')[1].split('"')[0]
                lng = line2.split('data-lng="')[1].split('"')[0]
        if "martin-center" in loc:
            hours = "Mon-Fri: 6 a.m.-9:30 p.m."
        if hours == "":
            hours = "<MISSING>"
        if "cox-north" in loc and "emergency" not in loc and "pharmacy" not in loc:
            hours = "Mon-Fri: 6:00pm - 7:00pm; Sat-Sun: 1:45pm - 3:15pm"
        if "branson-west" in loc:
            hours = "Monday-Thursday: 7 a.m.-5:45 p.m; Friday: 7 a.m.-4:45 p.m."
        if "cox-medical-center-south" in loc:
            hours = "General: 7 a.m. - 8:30 p.m. daily"
        if "meyer-ortho" in loc:
            hours = "Sun-Sat: 10:30 a.m. - 8:30 p.m"
        if "525" in add and "Branson" in city:
            hours = "General: 7 a.m. - 9 p.m. daily"
        if "2900" in add and "Springfield" in city:
            hours = "Monday-Friday: 8 a.m.-8 p.m."
        try:
            hours1 = hours.rsplit(";", 1)[0]
            hours2 = hours.rsplit(";", 1)[1]
            if (
                "0" not in hours2
                and "1" not in hours2
                and "2" not in hours2
                and "3" not in hours2
                and "4" not in hours2
                and "5" not in hours2
                and "6" not in hours2
                and "7" not in hours2
                and "8" not in hours2
                and "9" not in hours2
            ):
                hours = hours1
        except:
            pass
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
