import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("goldfishswimschool_com")


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
    url = "https://www.goldfishswimschool.com/SiteMap.xml"
    r = session.get(url, headers=headers)
    website = "goldfishswimschool.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if (
            "/contact-us/</loc>" in line
            and "//www.goldfishswimschool.com/contact-us/" not in line
        ):
            locs.append(line.split("<loc>")[1].split("/contact")[0])
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
        daycount = 0
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'mob-loc" href="tel:' in line2:
                phone = line2.split('mob-loc" href="tel:')[1].split('"')[0]
            if 'data-address="' in line2:
                try:
                    name = line2.split('data-businessname="')[1].split('"')[0]
                    add = line2.split('data-address="')[1].split('"')[0]
                    city = line2.split('data-city="')[1].split('"')[0]
                    state = line2.split('data-state="')[1].split('"')[0]
                    zc = line2.split('data-zip="')[1].split('"')[0]
                    lat = line2.split('data-latitude="')[1].split('"')[0]
                    lng = line2.split('data-longitude="')[1].split('"')[0]
                except:
                    name = ""
            if "day:" in line2:
                daycount = daycount + 1
                if 'class="closed">' in line2:
                    hrs = line2.split('class="closed">')[1].split(":")[0] + ": Closed"
                else:
                    hrs = line2.split(">")[1].split("<")[0]
                if daycount <= 7:
                    if hours == "":
                        hours = hrs
                    else:
                        hours = hours + "; " + hrs
        if hours == "":
            hours = "<MISSING>"
        if name != "":
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
