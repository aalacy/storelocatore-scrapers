import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("theburgerspriest_com")


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
    url = "https://theburgerspriest.com/find-a-location/"
    r = session.get(url, headers=headers)
    website = "theburgerspriest.com"
    typ = "<MISSING>"
    country = "CA"
    store = "<MISSING>"
    zc = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"name" : "' in line:
            name = line.split('"name" : "')[1].split('"')[0]
        if '"address" :"' in line:
            add = line.split('"address" :"')[1].split('"')[0]
        if '"city"  :"' in line:
            city = line.split('"city"  :"')[1].split('"')[0]
        if '"provShort" : "' in line:
            state = line.split('"provShort" : "')[1].split('"')[0]
        if '"phone" : "' in line:
            phone = line.split('"phone" : "')[1].split('"')[0]
        if '"coordinates":  [ "' in line:
            lng = line.split('"coordinates":  [ "')[1].split('"')[0]
            lat = line.split('" , "')[1].split('"')[0]
            name = ""
            add = ""
            city = ""
            state = ""
            hours = ""
            phone = ""
        if 'day : "' in line:
            day = line.split('day : "')[1].split('"')[0]
        if 'open : "' in line:
            ope = line.split('open : "')[1].split('"')[0]
        if 'close : "' in line:
            clo = line.split('close : "')[1].split('"')[0]
            if "Eve" not in day and "Day" not in day:
                hrs = day + ": " + ope + "-" + clo
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        if '"photo" :' in line:
            loc = "https://theburgerspriest.com/find-a-location/"
            if hours == "":
                hours = "<MISSING>"
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
