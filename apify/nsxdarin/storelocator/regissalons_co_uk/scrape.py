import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("regissalons_co_uk")


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
    url = "https://www.regissalons.co.uk/crb_store-sitemap.xml"
    r = session.get(url, headers=headers)
    website = "regissalons.co.uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://www.regissalons.co.uk/salon/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
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
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if name == "" and "<h3>" in line2:
                name = line2.split("<h3>")[1].split("<")[0]
            if '<p class="address">' in line2:
                addinfo = (
                    line2.split('<p class="address">')[1]
                    .split("</p>")[0]
                    .replace("<br />", "|")
                )
                if addinfo.count("|") == 3:
                    add = addinfo.split("|")[1]
                    city = addinfo.split("|")[2]
                    state = "<MISSING>"
                    zc = addinfo.split("|")[3]
                elif addinfo.count("|") == 4:
                    add = addinfo.split("|")[1] + " " + addinfo.split("|")[2]
                    city = addinfo.split("|")[3]
                    state = "<MISSING>"
                    zc = addinfo.split("|")[4]
            if 'href="tel:' in line2 and phone == "":
                phone = line2.split('href="tel:')[1].split('"')[0]
            if 'data-lat="' in line2:
                lat = line2.split('data-lat="')[1].split('"')[0]
                lng = line2.split('data-lng="')[1].split('"')[0]
            if "day</strong>" in line2 and "Today" not in line2:
                hrs = line2.split(">")[1].split("<")[0]
                next(lines)
                g = next(lines)
                g = str(g.decode("utf-8"))
                hrs = (
                    hrs
                    + ": "
                    + g.split("<")[0].strip().replace("\t", "").replace("&#8211;", "-")
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        if add != "":
            name = name.replace("&#038;", "&")
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
