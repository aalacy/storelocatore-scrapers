import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("childrenofamerica_com")


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
    url = "https://www.childrenofamerica.com/locations.cfm"
    r = session.get(url, headers=headers)
    website = "childrenofamerica.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'title="Daycare in ' in line:
            lurl = (
                "https://www.childrenofamerica.com/"
                + line.split('href="')[1].split('"')[0]
            )
            if lurl not in locs:
                locs.append(lurl)
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
                name = line2.split("<title>")[1].split("<")[0]
            if 'marginwidth="0" src="https://maps.google.com/maps/' in line2:
                try:
                    lat = line2.split("ll=")[1].split(",")[0]
                    lng = line2.split("ll=")[1].split(",")[1].split("&")[0]
                except:
                    lat = "<MISSING>"
                    lng = "<MISSING>"
            if ">GET DIRECTIONS<" in line2 and "ll=" in line2 and lat == "":
                try:
                    lat = line2.split("ll=")[1].split(",")[0]
                    lng = line2.split("ll=")[1].split(",")[1].split("&")[0]
                except:
                    lat = line2.split("ll=")[1].split("%")[0]
                    lng = line2.split("ll=")[1].split("%2C")[1].split("&")[0]
            if 'height="22" src="img/locationicon.png">' in line2:
                addinfo = line2.split('height="22" src="img/locationicon.png">')[
                    1
                ].split("</div>")[0]
                add = addinfo.split("<")[0].strip()
                city = addinfo.split("<br>")[1].split(",")[0]
                state = addinfo.split("<br>")[1].split(",")[1].strip().split(" ")[0]
                zc = addinfo.split("<br>")[1].rsplit(" ", 1)[1]
            if '></i> <a href="tel:' in line2:
                phone = line2.split('></i> <a href="tel:')[1].split('"')[0]
            if '<br><span class="text-style-2">Open:' in line2:
                hours = (
                    line2.split('<br><span class="text-style-2">Open:')[1]
                    .replace("\t", "")
                    .replace("\r", "")
                    .replace("\n", "")
                    .strip()
                    .replace("</span>", "")
                    .replace("<br>", "")
                    .replace('<span class="text-style-2">', "; ")
                )
        if lat == "":
            lat = "<MISSING>"
            lng = "<MISSING>"
        name = name.replace("Daycare in ", "")
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
