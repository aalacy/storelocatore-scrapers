import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("smokespoutinerie_com")


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
    url = "https://smokespoutinerie.com/wp-admin/admin-ajax.php?action=get_all_stores&lat=&lng="
    r = session.get(url, headers=headers)
    website = "smokespoutinerie.com"
    typ = "<MISSING>"
    country = "CA"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"gu":"' in line:
            items = line.split('"gu":"')
            for item in items:
                if ',"lat":"' in item:
                    st = item.split('"rg":"')[1].split('"')[0]
                    locs.append(item.split('"')[0].replace("\\", "") + "|" + st)
    for loc in locs:
        lurl = loc.split("|")[0]
        state = loc.split("|")[1]
        logger.info(lurl)
        name = ""
        add = ""
        city = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(lurl, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                name = line2.split("<title>")[1].split(" - ")[0].replace("&#39;", "'")
            if "<h3>ADDRESS</h3>" in line2:
                g = next(lines)
                h = next(lines)
                g = str(g.decode("utf-8"))
                h = str(h.decode("utf-8"))
                add = g.split(">")[1].split("<")[0]
                city = h.split(">")[1].split(",")[0]
                zc = h.split(",")[1].split("<")[0].strip()
            if 'class="storephone">' in line2:
                phone = line2.split('class="storephone">')[1].split("<")[0]
            if 'data-lat="' in line2:
                lat = line2.split('data-lat="')[1].split('"')[0]
            if 'data-lng="' in line2:
                lng = line2.split('data-lng="')[1].split('"')[0]
            if '<span class="day">' in line2:
                hrs = (
                    line2.split('<span class="day">')[1].split("<")[0]
                    + ": "
                    + line2.split('<span class="opentime">')[1].split("<")[0]
                    + line2.split('<span class="closetime">')[1].split("<")[0]
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        if "|" in name:
            name = name.split("|")[0].strip()
        name = name.replace("&#039;", "'")
        if "-" not in phone:
            phone = "<MISSING>"
        if "0" not in hours:
            hours = "<MISSING>"
        if "Centennial College Progress" in name:
            state = "Ontario"
            zc = "M1K 5E9"
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
