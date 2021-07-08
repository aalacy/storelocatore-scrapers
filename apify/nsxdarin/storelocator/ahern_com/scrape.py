import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("ahern_com")


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
    url = "https://www.ahern.com/assets/js/storeLocator/data/locations.json?formattedAddress=&boundsNorthEast=&boundsSouthWest="
    r = session.get(url, headers=headers)
    website = "ahern.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"web": "https://ahern.com/' in line:
            loc = line.split('"web": "')[1].split('"')[0]
        if '"id": "' in line:
            store = line.split('"id": "')[1].split('"')[0]
            name = ""
            lat = ""
            lng = ""
            loc = ""
            city = ""
            state = ""
            zc = ""
            phone = ""
            hours = ""
        if '"name": "' in line:
            name = line.split('"name": "')[1].split('"')[0]
        if '"lat": "' in line:
            lat = line.split('"lat": "')[1].split('"')[0]
        if '"lng": "' in line:
            lng = line.split('"lng": "')[1].split('"')[0]
        if '"category": "' in line:
            typ = line.split('"category": "')[1].split('"')[0]
        if '"city": "' in line:
            city = line.split('"city": "')[1].split('"')[0]
        if '"state": "' in line:
            state = line.split('"state": "')[1].split('"')[0]
        if '"postal": "' in line:
            zc = line.split('"postal": "')[1].split('"')[0]
        if '"phone": "' in line:
            phone = line.split('"phone": "')[1].split('"')[0]
        if '"hours1": "' in line:
            hours = line.split('"hours1": "')[1].split('"')[0]
        if '"hours2": "' in line and '"hours2": ""' not in line:
            hours = hours + "; " + line.split('"hours2": "')[1].split('"')[0]
        if '"hours3": "' in line and '"hours3": ""' not in line:
            hours = hours + "; " + line.split('"hours3": "')[1].split('"')[0]
        if '"address": "' in line:
            add = line.split('"address": "')[1].split('"')[0]
        if '"address2": "' in line:
            add = add + " " + line.split('"address2": "')[1].split('"')[0]
            add = add.strip()
        if '"attributes": "' in line:
            hours = hours.strip()
            if hours == "":
                hours = "<MISSING>"
            phone = phone.replace("Phone:", "").strip().replace("phone:", "")
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
