import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("choicehotels_com__en-uk__mainstay")


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
    url = "https://www.choicehotels.com/cs/chcom_eu/eu/docs/en-gb/choice-hotels/sitemap.xml"
    r = session.get(url, headers=headers, verify=False)
    website = "choicehotels.com/en-uk/mainstay"
    country = "GB"
    typ = "Mainstay"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "united-kingdom" in line and "mainstay-hotels/gb" in line:
            locs.append(
                line.strip().replace("\r", "").replace("\n", "").replace("\n", "")
            )
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = loc.split("mainstay-hotels/")[1]
        phone = ""
        lat = ""
        lng = ""
        hours = "<MISSING>"
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'window.hotelInfoData = {"status":"OK"' in line2:
                name = line2.split('"name":"')[1].split('"')[0]
                city = line2.split('"city":"')[1].split('"')[0]
                state = line2.split('"subdivision":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                lat = line2.split('"lat":"')[1].split('"')[0]
                lng = line2.split('"lon":"')[1].split('"')[0]
                add = line2.split('"line1":"')[1].split('"')[0]
                try:
                    phone = line2.split('"phone":"')[1].split('"')[0]
                except:
                    phone = "NA"
        if zc == "":
            zc = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if lat == "":
            lat = "<MISSING>"
            lng = "<MISSING>"
        if state == "":
            state = "<MISSING>"
        if phone != "NA":
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
