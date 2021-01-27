import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("loyalcompanion_com")


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
    url = "https://loyalcompanion.com/apps/store-locator"
    r = session.get(url, headers=headers)
    website = "loyalcompanion.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<a href='https://loyalcompanion.com/a/pages/locations" in line:
            items = line.split("<a href='https://loyalcompanion.com/a/pages/locations")
            for item in items:
                if (
                    "target='_blank'>https://loyalcompanion.com/a/pages/locations/"
                    in item
                ):
                    locs.append(
                        "https://loyalcompanion.com/a/pages/locations"
                        + item.split("'")[0]
                    )
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = loc.split("locations/")[1].split("/")[0]
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "position: {lat: " in line2:
                lat = line2.split("position: {lat: ")[1].split(",")[0]
                lng = line2.split("lng:")[1].split("}")[0].strip()
            if '<h1 itemprop="name">' in line2:
                name = line2.split('<h1 itemprop="name">')[1].split("<")[0]
            if 'itemprop="streetAddress">' in line2:
                add = line2.split('itemprop="streetAddress">')[1].split("<")[0]
            if 'itemprop="addressLocality">' in line2:
                city = line2.split('itemprop="addressLocality">')[1].split("<")[0]
            if 'itemprop="addressRegion">' in line2:
                state = line2.split('itemprop="addressRegion">')[1].split("<")[0]
            if 'itemprop="postalCode">' in line2:
                zc = line2.split('itemprop="postalCode">')[1].split("<")[0]
            if '="telephone"><a href="tel:' in line2:
                phone = (
                    line2.split('="telephone"><a href="tel:')[1]
                    .split('"')[0]
                    .replace("+1", "")
                )
            if '<div itemprop="openingHours" content="' in line2:
                hrs = line2.split('<div itemprop="openingHours" content="')[1].split(
                    '"'
                )[0]
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
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
