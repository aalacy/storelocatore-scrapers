import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers2 = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/json;charset=UTF-8",
    "s": "mjA1AiWID8JqImr3iMoEXFUpeuasRBIglY+FBqETplI=",
}
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("portillos_com")


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
    url = "https://www.portillos.com/ajax/location/getAllLocations/"
    payload = {"locations": [], "all": "y"}
    r = session.post(url, headers=headers2, data=json.dumps(payload))
    website = "portillos.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '{"Id":' in line:
            items = line.split('{"Id":')
            for item in items:
                if ',"Url":"' in item:
                    llat = item.split('"Lat":"')[1].split('"')[0]
                    llng = item.split('"Lng":"')[1].split('"')[0]
                    sid = item.split(",")[0]
                    locs.append(
                        "https://www.portillos.com"
                        + item.split(',"Url":"')[1].split('"')[0]
                        + "|"
                        + sid
                        + "|"
                        + llat
                        + "|"
                        + llng
                    )
    for loc in locs:
        lurl = loc.split("|")[0]
        logger.info(lurl)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = loc.split("|")[1]
        phone = ""
        lat = loc.split("|")[2]
        lng = loc.split("|")[3]
        hours = ""
        r2 = session.get(lurl, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "<h2>" in line2:
                name = line2.split("<h2>")[1].split("<")[0]
            if 'data-yext-field="address1"' in line2:
                add = (
                    line2.split('data-yext-field="address1"')[1]
                    .split(">")[1]
                    .split("<")[0]
                )
            if 'data-yext-field="city"' in line2:
                city = line2.split('">')[1].split("<")[0]
                state = line2.split('field="state"')[1].split(">")[1].split("<")[0]
                zc = line2.split('="zip"')[1].split(">")[1].split("<")[0]
            if 'data-yext-field="phone"' in line2:
                phone = (
                    line2.split('data-yext-field="phone"')[1]
                    .split(">")[1]
                    .split("<")[0]
                )
            if '"hours-sunday" data-yext-id="4">' in line2:
                h1 = (
                    "Sun: "
                    + line2.split('"hours-sunday" data-yext-id="4">')[1].split("<")[0]
                )
            if '"hours-monday" data-yext-id="4">' in line2:
                h2 = (
                    "Mon: "
                    + line2.split('"hours-monday" data-yext-id="4">')[1].split("<")[0]
                )
            if '"hours-tuesday" data-yext-id="4">' in line2:
                h3 = (
                    "Tue: "
                    + line2.split('"hours-tuesday" data-yext-id="4">')[1].split("<")[0]
                )
            if '"hours-wednesday" data-yext-id="4">' in line2:
                h4 = (
                    "Wed: "
                    + line2.split('"hours-wednesday" data-yext-id="4">')[1].split("<")[
                        0
                    ]
                )
            if '"hours-thursday" data-yext-id="4">' in line2:
                h5 = (
                    "Thu: "
                    + line2.split('"hours-thursday" data-yext-id="4">')[1].split("<")[0]
                )
            if '"hours-friday" data-yext-id="4">' in line2:
                h6 = (
                    "Fri: "
                    + line2.split('"hours-friday" data-yext-id="4">')[1].split("<")[0]
                )
            if '"hours-saturday" data-yext-id="4">' in line2:
                h7 = (
                    "Sat: "
                    + line2.split('"hours-saturday" data-yext-id="4">')[1].split("<")[0]
                )
            if "</html>" in line2:
                hours = (
                    h1
                    + "; "
                    + h2
                    + "; "
                    + h3
                    + "; "
                    + h4
                    + "; "
                    + h5
                    + "; "
                    + h6
                    + "; "
                    + h7
                )
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
