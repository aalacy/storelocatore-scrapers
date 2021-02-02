import csv
import re
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded",
}

logger = SgLogSetup().get_logger("stelizabeth_com")


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
    url = "https://stelizabeth.com/find-a-location/Search"
    payload = {
        "SearchLat": "",
        "SearchLong": "",
        "SearchArea": "41011",
        "SearchText": "",
    }
    r = session.post(url, headers=headers, data=payload)
    website = "stelizabeth.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'class="loc-rsl-location-name loc-rsl-show-lg">' in line:
            locs.append(
                "https://stelizabeth.com" + line.split('href="')[1].split('"')[0]
            )
    for loc in locs:
        logger.info(loc)
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
        HFound = False
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<h2 class="loc-det-location-name">' in line2:
                name = line2.split('<h2 class="loc-det-location-name">')[1].split("<")[
                    0
                ]
                if " - " in name:
                    typ = name.split(" - ")[0]
                    name = name.split(" - ")[1]
            if '="street-address">' in line2:
                add = line2.split('="street-address">')[1].split("<")[0]
            if '="locality">' in line2:
                city = line2.split('="locality">')[1].split("<")[0]
            if '="region">' in line2:
                state = line2.split('="region">')[1].split("<")[0]
            if '="postal-code">' in line2:
                zc = line2.split('="postal-code">')[1].split("<")[0]
            if "Hours:" in line2:
                HFound = True
            if HFound and "</div>" in line2:
                HFound = False
            if HFound and "Hours:" not in line2:
                hrs = (
                    line2.strip()
                    .replace("\r", "")
                    .replace("\t", "")
                    .replace("\n", "")
                    .replace("<br>", "; ")
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if " PM" in line2:
                hrs = (
                    line2.replace("<br />", "")
                    .replace("\t", "")
                    .replace("\n", "")
                    .replace("\r", "")
                    .strip()
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if " pm" in line2:
                hrs = (
                    line2.replace("<br />", "")
                    .replace("\t", "")
                    .replace("\n", "")
                    .replace("\r", "")
                    .strip()
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if " p.m." in line2:
                hrs = (
                    line2.replace("<br />", "")
                    .replace("\t", "")
                    .replace("\n", "")
                    .replace("\r", "")
                    .strip()
                    .replace("<strong>", "")
                    .replace("</strong>", "")
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if "<br>Tue:" in line2 and "<br>Thu:" in line2:
                hours = (
                    line2.strip().replace("\r", "").replace("\t", "").replace("\n", "")
                )
        hours = (
            hours.replace("<br>", "; ")
            .replace("  ", " ")
            .replace("<div>", "")
            .replace("</div>", "")
            .replace("&amp;", "&")
            .replace("&ndash;", "-")
        )
        cleanr = re.compile("<.*?>")
        hours = re.sub(cleanr, "", hours)
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if add != "":
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
