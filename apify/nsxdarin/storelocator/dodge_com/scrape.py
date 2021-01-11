import csv
from sgrequests import SgRequests
import sgzip
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("dodge_com")


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
    ids = []
    for code in sgzip.for_radius(50):
        logger.info("Pulling Zip Code %s..." % code)
        url = (
            "https://www.dodge.com/bdlws/MDLSDealerLocator?brandCode=D&func=SALES&radius=50&resultsPage=1&resultsPerPage=100&zipCode="
            + code
        )
        r = session.get(url, headers=headers)
        lines = r.iter_lines()
        for line in lines:
            line = str(line.decode("utf-8"))
            if '"dealerCode" : "' in line:
                store = line.split('"dealerCode" : "')[1].split('"')[0]
                website = "dodge.com"
                typ = "Dealer"
                country = "US"
                hours = ""
                add = ""
                name = ""
                state = ""
                city = ""
                phone = ""
                lat = ""
                lng = ""
            if '"dealerName" : "' in line:
                name = line.split('"dealerName" : "')[1].split('"')[0]
            if '"dealerAddress1" : "' in line:
                add = line.split('"dealerAddress1" : "')[1].split('"')[0]
            if '"dealerAddress2" : "' in line:
                add = add + " " + line.split('"dealerAddress2" : "')[1].split('"')[0]
                add = add.strip()
            if '"dealerState" : "' in line:
                state = line.split('"dealerState" : "')[1].split('"')[0]
            if '"dealerCity" : "' in line:
                city = line.split('"dealerCity" : "')[1].split('"')[0]
            if '"dealerZipCode" : "' in line:
                zc = line.split('"dealerZipCode" : "')[1].split('"')[0]
            if '"website" : "' in line:
                purl = line.split('"website" : "')[1].split('"')[0]
            if '"phoneNumber" : "' in line:
                phone = line.split('"phoneNumber" : "')[1].split('"')[0]
            if '"dealerShowroomLongitude" : "' in line:
                lng = line.split('"dealerShowroomLongitude" : "')[1].split('"')[0]
            if '"dealerShowroomLatitude" : "' in line:
                lat = line.split('"dealerShowroomLatitude" : "')[1].split('"')[0]
            if 'day"' in line:
                dayname = line.split('"')[1].title()
                next(lines)
                next(lines)
                next(lines)
                g = next(lines)
                h = next(lines)
                g = str(g.decode("utf-8"))
                h = str(h.decode("utf-8"))
                hours = (
                    hours
                    + "; "
                    + dayname
                    + ": "
                    + g.split('"time" : "')[1].split('"')[0]
                    + h.split('"ampm" : "')[1].split('"')[0]
                )
                next(lines)
                next(lines)
                g = next(lines)
                h = next(lines)
                g = str(g.decode("utf-8"))
                h = str(h.decode("utf-8"))
                hours = (
                    hours
                    + "-"
                    + g.split('"time" : "')[1].split('"')[0]
                    + h.split('"ampm" : "')[1].split('"')[0]
                )
            if '"service"' in line:
                if len(zc) == 9:
                    zc = zc[:5] + "-" + zc[-4:]
                if purl == "":
                    purl = "<MISSING>"
                if store not in ids:
                    ids.append(store)
                    hours = hours.replace("Sunday: 0:00AM-0:00AM", "Sunday: Closed")
                    yield [
                        website,
                        purl,
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
