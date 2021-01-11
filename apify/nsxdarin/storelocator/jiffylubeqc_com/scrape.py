# -*- coding: cp1252 -*-
import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("jiffylubeqc_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded",
}
headers2 = {
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
    url = "https://jiffylubeqc.com/succursales/trouver-une-succursale/"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if (
            'menu-item-depth-1" value="https://jiffylubeqc.com/succursales/' in line
            and "Trouver votre su" not in line
            and "Calendrier" not in line
        ):
            locs.append(
                "https://jiffylubeqc.com/succursales/"
                + line.split(
                    'menu-item-depth-1" value="https://jiffylubeqc.com/succursales/'
                )[1].split('"')[0]
            )
    for loc in locs:
        logger.info("Pulling Location %s..." % loc)
        zc = ""
        city = ""
        website = "jiffylubeqc.com"
        country = "CA"
        state = "QC"
        typ = "<MISSING>"
        HFound = False
        hours = ""
        add = ""
        lat = "<MISSING>"
        lng = "<MISSING>"
        phone = ""
        store = "<MISSING>"
        name = ""
        r2 = session.get(loc, headers=headers2)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "<p><strong>" in line2:
                name = line2.split("<p><strong>")[1].split("<")[0]
                g = next(lines)
                h = next(lines)
                g = str(g.decode("utf-8"))
                h = str(h.decode("utf-8"))
                add = g.split("<")[0]
                city = h.split(",")[0]
                zc = h.split(",")[1].split("<")[0].strip()
            if "new google.maps.LatLng(" in line2:
                lat = line2.split("new google.maps.LatLng(")[1].split(",")[0]
                lng = (
                    line2.split("new google.maps.LatLng(")[1]
                    .split(",")[1]
                    .split(")")[0]
                )
            if "phone : <strong>" in line2:
                phone = line2.split("phone : <strong>")[1].split("<")[0]
            if "<h2>Heures d&rsquo;ouverture</h2>" in line2:
                HFound = True
            if HFound and "<h2>Cartes" in line2:
                HFound = False
            if HFound and "<h2>" not in line2:
                hrs = (
                    line2.replace("\r", "").replace("\t", "").replace("\n", "").strip()
                )
                hrs = hrs.replace("<br />", "").replace("<p>", "").replace("</p>", "")
                hrs = hrs.replace("<strong>", "").replace("</strong>", "")
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        if phone == "":
            phone = "<MISSING>"
        hours = (
            hours.replace(" à ", "-")
            .replace("Du ", "")
            .replace("Lundi au Vendredi", "Mon-Fri")
            .replace("Samedi", "Saturday")
            .replace("Dimanche", "Sunday")
        )
        hours = (
            hours.replace("Lundi", "Mon")
            .replace("Mardi", "Tue")
            .replace("mercredi", "Wed")
            .replace("Jeudi", "Thu")
            .replace("Vendredi", "Fri")
        )
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
