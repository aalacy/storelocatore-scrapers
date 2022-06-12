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
    states = []
    cities = []
    url = "https://stores.maccosmetics.com/us"
    r = session.get(url, headers=headers)
    website = "maccosmetics.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"Directory-listLink" href="' in line:
            items = line.split('"Directory-listLink" href="')
            for item in items:
                if 'data-ya-track="directorylink" data-count="(' in item:
                    lurl = "https://stores.maccosmetics.com/" + item.split('"')[0]
                    count = item.split('data-ya-track="directorylink" data-count="(')[
                        1
                    ].split(")")[0]
                    if count == "1":
                        locs.append(lurl)
                    else:
                        states.append(lurl)
    for state in states:
        logger.info(state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '"Directory-listLink" href="../' in line2:
                items = line2.split('"Directory-listLink" href="../')
                for item in items:
                    if 'data-ya-track="directorylink" data-count="(' in item:
                        lurl = "https://stores.maccosmetics.com/" + item.split('"')[0]
                        count = item.split(
                            'data-ya-track="directorylink" data-count="('
                        )[1].split(")")[0]
                        if count == "1":
                            locs.append(lurl)
                        else:
                            cities.append(lurl)
    for city in cities:
        logger.info(city)
        r2 = session.get(city, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '"Teaser-titleLink" href="../../' in line2:
                items = line2.split('"Teaser-titleLink" href="../../')
                for item in items:
                    if 'data-ya-track="businessname"' in item:
                        locs.append(
                            "https://stores.maccosmetics.com/" + item.split('"')[0]
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
            if '<td class="c-hours-details-row-day">' in line2 and hours == "":
                days = line2.split('<td class="c-hours-details-row-day">')
                for day in days:
                    if '</td><td class="c-hours-details-row-intervals">' in day:
                        if 'data-open-interval-start="' not in day:
                            hrs = (
                                day.split("<")[0]
                                + ": "
                                + day.split(
                                    '</td><td class="c-hours-details-row-intervals">'
                                )[1].split("<")[0]
                            )
                        else:
                            hrs = (
                                day.split("<")[0]
                                + ": "
                                + day.split('data-open-interval-start="')[1].split('"')[
                                    0
                                ]
                                + "-"
                                + day.split('data-open-interval-end="')[1].split('"')[0]
                            )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
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
