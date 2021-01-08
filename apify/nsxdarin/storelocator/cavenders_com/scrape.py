import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("cavenders_com")


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
    url = "https://www.cavenders.com/storelocator"
    r = session.get(url, headers=headers)
    website = "cavenders.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    store = "<MISSING>"
    hours = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    logger.info("Pulling Stores")
    lines = r.iter_lines()
    for line in lines:
        line = str(line.decode("utf-8"))
        if '<span class="store-name">' in line:
            add = ""
            city = ""
            state = ""
            zc = ""
            phone = ""
            hours = ""
            store = ""
            name = (
                line.split('<span class="store-name">')[1]
                .split("<")[0]
                .replace("&#39;", "'")
            )
        if '<a href="tel:' in line:
            phone = (
                line.split('<a href="tel:')[1]
                .split('"')[0]
                .replace("&#40;", "(")
                .replace("&#41;", ")")
            )
        if "DAY</span></td>" in line and "</strong>" not in line:
            day = line.split('">')[1].split("<")[0]
            g = next(lines)
            g = str(g.decode("utf-8"))
            if ">CLOSE</td>" not in g:
                day = day + ": " + g.split('11px;">')[1].split("<")[0]
                g = next(lines)
                g = str(g.decode("utf-8"))
                day = day + "-" + g.split('11px;">')[1].split("<")[0]
                if hours == "":
                    hours = day
                else:
                    hours = hours + "; " + day
            else:
                day = day + " CLOSED"
                if hours == "":
                    hours = day
                else:
                    hours = hours + "; " + day
        if '"address1": "' in line:
            add = line.split('"address1": "')[1].split('"')[0]
        if '"city":"' in line:
            city = line.split('"city":"')[1].split('"')[0]
        if '"stateCode":"' in line:
            state = line.split('"stateCode":"')[1].split('"')[0]
        if '"postalCode":"' in line:
            zc = line.split('"postalCode":"')[1].split('"')[0]
        if '"storeID":"' in line:
            store = line.split('"storeID":"')[1].split('"')[0]
        if '"longitude":' in line:
            lng = line.split('"longitude":"')[1].split('"')[0]
        if '"latitude":' in line:
            lat = line.split('"latitude":"')[1].split('"')[0]
        if '"detailPage":"' in line:
            loc = (
                "https://www.cavenders.com"
                + line.split('"detailPage":"')[1].split('"')[0]
            )
        if '"index":""' in line:
            if phone == "":
                phone = "<MISSING>"
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
