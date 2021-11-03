import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("accessstorage_com")


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
    urls = [
        "https://www.accessstorage.com/stores-outside-london",
        "https://www.accessstorage.com/stores-in-london",
    ]
    website = "accessstorage.com"
    typ = "<MISSING>"
    country = "GB"
    for url in urls:
        r = session.get(url, headers=headers)
        logger.info("Pulling Stores")
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if 'store-link" href="https://' in line:
                locs.append(line.split('href="')[1].split('"')[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if '"name": "' in line2:
                name = line2.split('"name": "')[1].split('"')[0]
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if 'times__label">' in line2:
                g = next(lines)
                g = str(g.decode("utf-8"))
                day = g.strip().replace("\r", "").replace("\t", "").replace("\n", "")
            if 'store-opening-times__hours">' in line2:
                g = next(lines)
                g = str(g.decode("utf-8"))
                hrs = (
                    day
                    + ": "
                    + g.strip().replace("\r", "").replace("\t", "").replace("\n", "")
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if '"store-map__info-address">' in line2:
                add = line2.split('"store-map__info-address">')[1].split("<")[0]
            if 'banner__info-address">' in line2:
                g = next(lines)
                g = str(g.decode("utf-8"))
                state = "<MISSING>"
                if g.count(",") == 2:
                    city = g.split(",")[1].strip()
                elif g.count(",") == 3:
                    city = g.split(",")[2].strip()
                else:
                    city = g.split(",")[3].strip()
            if 'data-lat="' in line2:
                lat = line2.split('data-lat="')[1].split('"')[0]
                lng = line2.split('data-lng="')[1].split('"')[0]
        if "/access-self-storage-guildford" in loc:
            add = "19 Moorfield Road, Slyfield Industrial Estate"
        hours = hours.replace("Monday - Friday: ;", "Monday - Friday: 08.00 - 18.00")
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
