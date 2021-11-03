import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("rogersandhollands_com")


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
    url = "https://rogersandhollands.com/ustorelocator/location/map"
    r = session.get(url, headers=headers)
    website = "rogersandhollands.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "initial_locations:" in line:
            items = line.split('{"location_id":"')
            for item in items:
                if ',"title":"' in item:
                    store = item.split('"')[0]
                    hours = ""
                    name = item.split(',"title":"')[1].split('"')[0]
                    addinfo = item.split('"address":"')[1].split('"')[0]
                    lat = item.split('"latitude":"')[1].split('"')[0]
                    lng = item.split('"longitude":"')[1].split('"')[0]
                    loc = (
                        item.split('"website_url":"')[1].split('"')[0].replace("\\", "")
                    )
                    phone = item.split('"phone":"')[1].split('"')[0]
                    r2 = session.get(loc, headers=headers)
                    logger.info(loc)
                    for line2 in r2.iter_lines():
                        line2 = str(line2.decode("utf-8"))
                        if "pm<" in line2:
                            hours = (
                                line2.split("<p>")[1]
                                .split("</p>")[0]
                                .replace("<br>", "; ")
                            )
                    add = addinfo.split(",")[0]
                    city = addinfo.split(",")[1].strip()
                    state = addinfo.split(",")[2].strip().split(" ")[0]
                    zc = addinfo.rsplit(" ", 1)[1]
                    if zc == "":
                        zc = "<MISSING>"
                    if "1600 Mid Rivers Mall" in add:
                        zc = "63376"
                    add = add.replace("\\u2013", "-")
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
