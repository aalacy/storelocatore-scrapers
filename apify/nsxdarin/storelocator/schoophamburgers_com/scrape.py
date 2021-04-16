import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("schoophamburgers_com")


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
    url = "https://www.schoophamburgers.com/locations"
    r = session.get(url, headers=headers)
    website = "schoophamburgers.com"
    typ = "<MISSING>"
    country = "US"
    loc = "https://www.schoophamburgers.com/locations"
    store = "<MISSING>"
    hours = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    name = "Warsaw, IN"
    city = "Warsaw"
    state = "IN"
    phone = "574-268-9500"
    add = "3501 Lake City Hwy"
    zc = "46580"
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
    add = ""
    city = ""
    state = ""
    zc = ""
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'class="font-size-26 lh-1">' in line:
            name = line.split('class="font-size-26 lh-1">')[1].split("<")[0]
        if (
            '<span class="text" id="' in line
            and "iew Map</span>" not in line
            and "VIEW ALL LOCATIONS" not in line
        ):
            phone = line.split('">')[1].split("<")[0]
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
        if 'class="font-size-14 lh-1">' in line:
            addinfo = line.split('class="font-size-14 lh-1">')[1].split("<")[0]
            addinfo = addinfo.replace("Dr Orland", "Dr, Orland").replace("&nbsp;", "")
            add = addinfo.split(",")[0]
            city = addinfo.split(",")[1].strip()
            state = addinfo.split(",")[2].strip().split(" ")[0]
            zc = addinfo.split(",")[2].rsplit(" ", 1)[1]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
