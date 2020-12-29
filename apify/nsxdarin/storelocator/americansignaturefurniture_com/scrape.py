import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("americansignaturefurniture_com")


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
    url = "https://www.americansignaturefurniture.com/store-locator/show-all-locations"
    r = session.get(url, headers=headers)
    website = "americansignaturefurniture.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "Store Details</a>" in line:
            locs.append(
                "https://www.americansignaturefurniture.com/"
                + line.split('href="')[1].split('"')[0]
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
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'store-name-breadcrumb" itemprop="title">' in line2:
                name = (
                    line2.split('store-name-breadcrumb" itemprop="title">')[1]
                    .split("<")[0]
                    .strip()
                )
            if 'itemprop="streetAddress">' in line2 and add == "":
                add = line2.split('itemprop="streetAddress">')[1].split("<")[0].strip()
            if 'itemprop="addressLocality">' in line2 and city == "":
                city = (
                    line2.split('itemprop="addressLocality">')[1].split("<")[0].strip()
                )
            if 'itemprop="addressRegion">' in line2 and state == "":
                state = (
                    line2.split('itemprop="addressRegion">')[1].split("<")[0].strip()
                )
            if 'itemprop="postalCode">' in line2 and zc == "":
                zc = line2.split('itemprop="postalCode">')[1].split("<")[0].strip()
            if 'phone-number" href="tel:' in line2 and phone == "":
                phone = line2.split('phone-number" href="tel:')[1].split('"')[0].strip()
            if 'itemprop="openingHours" datetime="' in line2:
                hrs = (
                    line2.split('itemprop="openingHours" datetime="')[1]
                    .split('"')[0]
                    .strip()
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        city = city.replace(",", "")
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
