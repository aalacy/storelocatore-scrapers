import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("maccosmetics_com")


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
    url = "https://stores.maccosmetics.com/sitemap.xml"
    r = session.get(url, headers=headers)
    website = "maccosmetics.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://stores.maccosmetics.com/us/" in line:
            lurl = line.split(">")[1].split("<")[0]
            if lurl.count("/") == 6:
                locs.append(lurl)
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
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'id="location-name">' in line2:
                name = line2.split('id="location-name">')[1].split("<")[0]
            if '"c-address-street-1">' in line2 and add == "":
                add = line2.split('"c-address-street-1">')[1].split("<")[0]
                try:
                    add = (
                        add
                        + " "
                        + line2.split('"c-address-street-2">')[1].split("<")[0]
                    )
                    add = add.strip()
                except:
                    pass
                city = line2.split('class="c-address-city">')[1].split("<")[0]
                state = line2.split('itemprop="addressRegion">')[1].split("<")[0]
                zc = line2.split('"postalCode">')[1].split("<")[0]
                phone = line2.split('id="phone-main"><span>')[1].split("<")[0]
            if 'itemprop="latitude" content="' in line2:
                lat = line2.split('itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('"longitude" content="')[1].split('"')[0]
            if hours == "" and '{"day":"' in line2:
                days = (
                    line2.split("days='")[1]
                    .split("}]' data-utc-offsets")[0]
                    .split('{"day":"')
                )
                for day in days:
                    if '"isClosed"' in day:
                        dname = day.split('"')[0]
                        if '"isClosed":true' in day:
                            hrs = dname + ": Closed"
                        else:
                            hrs = (
                                dname
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
        name = name.replace("&#39;", "'")
        add = add.replace("&#39;", "'")
        if "90-15-queens-blvd" in loc:
            name = "Queens Center"
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
