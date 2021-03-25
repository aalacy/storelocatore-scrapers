import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("basspro_com")


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
    url = "https://stores.basspro.com/"
    r = session.get(url, headers=headers)
    website = "basspro.com"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<a class="location-card-title-link" href="' in line:
            items = line.split('<a class="location-card-title-link" href="')
            for item in items:
                if '<h2 class="location-card-title">' in item:
                    locs.append(item.split('"')[0])
    for loc in locs:
        typ = "Bass Pro"
        if "cabelas." in loc:
            typ = "Cabela's"
        country = "US"
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
        if ".ca" in loc:
            country = "CA"
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<h1 class="heading heading-largest">' in line2:
                name = line2.split('<h1 class="heading heading-largest">')[1].split(
                    "<"
                )[0]
            if '<span itemprop="telephone">' in line2:
                phone = line2.split('<span itemprop="telephone">')[1].split("<")[0]
            if '<p itemprop="openingHours" content="' in line2:
                hrs = line2.split('<p itemprop="openingHours" content="')[1].split('"')[
                    0
                ]
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if '<span><span itemprop="addressLocality">' in line2:
                city = line2.split('<span><span itemprop="addressLocality">')[1].split(
                    "<"
                )[0]
            if '<span itemprop="addressRegion">' in line2:
                state = line2.split('<span itemprop="addressRegion">')[1].split("<")[0]
                zc = line2.split('itemprop="postalCode">')[1].split("<")[0]
            if '<span itemprop="streetAddress"><strong>' in line2:
                add = (
                    line2.split('<span itemprop="streetAddress"><strong>')[1]
                    .split("<")[0]
                    .strip()
                )
            if 'content="https://www.google.com/maps/place/' in line2:
                try:
                    lat = line2.split("@")[1].split(",")[0]
                    lng = line2.split("@")[1].split(",")[1]
                except:
                    pass
            if 'property="og:title" content="' in line2:
                name = line2.split('property="og:title" content="')[1].split('"')[0]
                name = name.split(" |")[0]
            if '<span class="c-address-street-1">' in line2 and add == "":
                add = line2.split('<span class="c-address-street-1">')[1].split("<")[0]
                city = line2.split('"addressLocality">')[1].split("<")[0]
                state = line2.split('itemprop="addressRegion">')[1].split("<")[0]
                zc = line2.split('itemprop="postalCode">')[1].split("<")[0].strip()
                phone = line2.split('main-number-link" href="tel:+')[1].split('"')[0]
            if 'itemprop="latitude" content="' in line2:
                lat = line2.split('itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('itemprop="longitude" content="')[1].split('"')[0]
            if "Regular Store Hours</h3>" in line2 and hours == "":
                days = (
                    line2.split("Regular Store Hours</h3>")[1]
                    .split("data-days='[")[1]
                    .split("]}]")[0]
                    .split('"day":"')
                )
                for day in days:
                    if '"end":' in day:
                        hrs = (
                            day.split('"')[0]
                            + ": "
                            + day.split('"start":')[1].split("}")[0]
                            + "-"
                            + day.split('"end":')[1].split(",")[0]
                        )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
        if lat == "":
            lat = "<MISSING>"
        if lng == "":
            lng = "<MISSING>"
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
