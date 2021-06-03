import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("pret_co_uk")


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
    cities = []
    url = "https://locations.pret.co.uk/"
    r = session.get(url, headers=headers)
    website = "pret.co.uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<a class="Directory-listLink" href="' in line:
            items = line.split('<a class="Directory-listLink" href="')
            for item in items:
                if 'data-count="(' in item:
                    count = item.split('data-count="(')[1].split(")")[0]
                    if count == "1":
                        locs.append(
                            "https://locations.pret.co.uk/"
                            + item.split('"')[0].replace("&#39;", "'")
                        )
                    else:
                        cities.append(
                            "https://locations.pret.co.uk/"
                            + item.split('"')[0].replace("&#39;", "'")
                        )
    for city in cities:
        logger.info(city)
        r2 = session.get(city, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '="Teaser-titleLink" href="' in line2:
                items = line2.split('="Teaser-titleLink" href="')
                for item in items:
                    if 'data-ya-track="businessname">' in item:
                        locs.append(
                            "https://locations.pret.co.uk/"
                            + item.split('"')[0].replace("&#39;", "'")
                        )
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = "<MISSING>"
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'class="Hero-locationName" itemprop="name">' in line2:
                name = line2.split('class="Hero-locationName" itemprop="name">')[
                    1
                ].split("<")[0]
            if 'itemprop="latitude" content="' in line2:
                lat = line2.split('itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('itemprop="longitude" content="')[1].split('"')[0]
            if 'itemprop="streetAddress" content="' in line2:
                add = line2.split('itemprop="streetAddress" content="')[1].split('"')[0]
            if 'c-AddressRow> <span class="c-address-city">' in line2 and city == "":
                city = line2.split('c-AddressRow> <span class="c-address-city">')[
                    1
                ].split("<")[0]
                state = "<MISSING>"
            if 'itemprop="postalCode">' in line2:
                zc = line2.split('itemprop="postalCode">')[1].split("<")[0]
            if '="telephone" id="phone-main">' in line2:
                phone = line2.split('="telephone" id="phone-main">')[1].split("<")[0]
            if "js-hours-table\"  data-days='[" in line2:
                days = (
                    line2.split("js-hours-table\"  data-days='[")[1]
                    .split("]' data-utc")[0]
                    .split('"day":"')
                )
                for day in days:
                    if '"intervals"' in day:
                        if '"isClosed":true' in day:
                            hrs = day.split('"')[0] + ": Closed"
                        else:
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
        if phone == "":
            phone = "<MISSING>"
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
