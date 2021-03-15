import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("att_com")


session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


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
    states = []
    url = "https://www.att.com/stores/us"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<a class="Directory-listLink" href="' in line:
            items = line.split('<a class="Directory-listLink" href="')
            for item in items:
                if 'data-count="(' in item:
                    states.append("https://www.att.com/stores/" + item.split('"')[0])
    for state in states:
        logger.info(state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '"Directory-listLink" href="' in line2:
                items = line2.split('"Directory-listLink" href="')
                for item in items:
                    if 'data-count="(' in item:
                        count = item.split('data-count="(')[1].split(")")[0]
                        if count == "1":
                            locs.append(
                                "https://www.att.com/stores/" + item.split('"')[0]
                            )
                        else:
                            cities.append(
                                "https://www.att.com/stores/" + item.split('"')[0]
                            )
    for city in cities:
        logger.info(city)
        r2 = session.get(city, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<a class="Teaser-titleLink" href="../' in line2:
                items = line2.split('<a class="Teaser-titleLink" href="../')
                for item in items:
                    if 'data-ya-track="businessname">' in item:
                        locs.append("https://www.att.com/stores/" + item.split('"')[0])
    for loc in locs:
        logger.info("Pulling Location %s..." % loc)
        website = "att.com"
        typ = "Store"
        hours = ""
        lat = ""
        name = ""
        phone = ""
        store = loc.rsplit("/", 1)[1]
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'itemprop="streetAddress" content="' in line2:
                add = line2.split('itemprop="streetAddress" content="')[1].split('"')[0]
                city = line2.split('<meta itemprop="addressLocality" content="')[
                    1
                ].split('"')[0]
                country = "US"
                try:
                    state = line2.split('itemprop="addressRegion">')[1].split("<")[0]
                except:
                    state = ""
                zc = line2.split('itemprop="postalCode">')[1].split("<")[0]
            if name == "" and '"LocationName-brand">' in line2:
                name = (
                    line2.split('"LocationName-brand">')[1]
                    .split("<")[0]
                    .replace("&amp;", "&")
                )
            if lat == "" and '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[
                    0
                ]
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[
                    0
                ]
            if ' itemprop="telephone" id="phone-main">' in line2:
                phone = line2.split(' itemprop="telephone" id="phone-main">')[1].split(
                    "<"
                )[0]
            if 'itemprop="openingHours" content="' in line2:
                days = line2.split('itemprop="openingHours" content="')
                for day in days:
                    if 'id="location-name">' not in day:
                        hrs = day.split('"')[0]
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if "puerto-rico/" in loc:
            state = "PR"
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
