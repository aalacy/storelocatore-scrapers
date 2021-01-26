# -*- coding: cp1252 -*-
import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("capriottis_com")


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
    url = "https://order.capriottis.com/sitemap.xml"
    r = session.get(url, headers=headers)
    website = "capriottis.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://order.capriottis.com/menu/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = ""
        phone = ""
        lat = ""
        lng = ""
        HFound = False
        hours = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if 'var vendorName = "' in line2:
                name = line2.split('var vendorName = "')[1].split('"')[0]
            if 'var vendorStreetAddress = "' in line2:
                add = line2.split('var vendorStreetAddress = "')[1].split('"')[0]
            if 'var vendorCity = "' in line2:
                city = line2.split('var vendorCity = "')[1].split('"')[0]
            if 'var vendorState = "' in line2:
                state = line2.split('var vendorState = "')[1].split('"')[0]
            if "var vendorLatitude = " in line2:
                lat = line2.split("var vendorLatitude = ")[1].split(";")[0]
            if "var vendorLongitude = " in line2:
                lng = line2.split("var vendorLongitude = ")[1].split(";")[0]
            if "zipCode: '" in line2:
                zc = line2.split("zipCode: '")[1].split("'")[0]
            if 'span class="tel">' in line2:
                g = next(lines)
                g = str(g.decode("utf-8"))
                phone = g.strip().replace("\t", "").replace("\r", "").replace("\n", "")
            if "'Store ID': '" in line2:
                store = line2.split("'Store ID': '")[1].split("'")[0]
            if "Business Hours</span>" in line2:
                HFound = True
            if HFound and "</dl>" in line2:
                HFound = False
            if HFound and "day:" in line2:
                day = (
                    line2.split("<dt>")[1]
                    .split("</dt>")[0]
                    .replace("<strong>", "")
                    .replace("</strong>", "")
                )
                g = next(lines)
                g = str(g.decode("utf-8"))
                while "<dd>" not in g:
                    g = next(lines)
                    g = str(g.decode("utf-8"))
                hrs = (
                    day
                    + " "
                    + g.split("<dd>")[1]
                    .split("</dd>")[0]
                    .replace("<strong>", "")
                    .replace("</strong>", "")
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        name = name.replace("&#39;", "'").replace("’", "'").replace("&amp;", "&")
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
