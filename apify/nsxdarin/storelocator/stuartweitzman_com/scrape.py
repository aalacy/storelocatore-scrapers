import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("stuartweitzman_com")


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
    url = "https://ca.stuartweitzman.com/stores/"
    r = session.get(url, headers=headers)
    website = "stuartweitzman.com"
    typ = "<MISSING>"
    country = "CA"
    logger.info("Pulling Stores")
    states = []
    cities = []
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<a class="Directory-listLink" href="' in line:
            items = line.split('<a class="Directory-listLink" href="')
            for item in items:
                if 'data-count="(' in item:
                    count = item.split('data-count="(')[1].split(")")[0]
                    lurl = "https://ca.stuartweitzman.com/stores/" + item.split('"')[0]
                    if count == "1":
                        locs.append(lurl)
                    else:
                        states.append(lurl)
    for state in states:
        r2 = session.get(state, headers=headers)
        logger.info(state)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<a class="Directory-listLink" href="' in line2:
                items = line2.split('<a class="Directory-listLink" href="')
                for item in items:
                    if 'data-count="(' in item:
                        count = item.split('data-count="(')[1].split(")")[0]
                        if count == "1":
                            locs.append(
                                "https://ca.stuartweitzman.com/stores/"
                                + item.split('"')[0]
                            )
                        else:
                            cities.append(
                                "https://ca.stuartweitzman.com/stores/"
                                + item.split('"')[0]
                            )
            if '<a data-ya-track="visitpage" href="../' in line2:
                items = line2.split('<a data-ya-track="visitpage" href="../')
                for item in items:
                    if "Explore This Shop</a>" in item:
                        locs.append(
                            "https://ca.stuartweitzman.com/stores/" + item.split('"')[0]
                        )
    for city in cities:
        r2 = session.get(city, headers=headers)
        logger.info(city)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<a data-ya-track="visitpage" href="../' in line2:
                items = line2.split('<a data-ya-track="visitpage" href="../')
                for item in items:
                    if "Explore This Shop</a>" in item:
                        locs.append(
                            "https://ca.stuartweitzman.com/stores/" + item.split('"')[0]
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
            if 'geo Heading--lead">' in line2:
                name = line2.split('geo Heading--lead">')[1].split("<")[0]
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[
                    0
                ]
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[
                    0
                ]
            if '<span class="c-address-street-1">' in line2 and add == "":
                addinfo = line2.split('<span class="c-address-street-1">')[1].split(
                    'itemprop="addressCountry">'
                )[0]
                add = addinfo.split("<")[0]
                try:
                    add = (
                        add
                        + " "
                        + addinfo.split('<span class="c-address-street-2">')[1].split(
                            "<"
                        )[0]
                    )
                except:
                    pass
                city = addinfo.split('address-city">')[1].split("<")[0]
                state = addinfo.split('itemprop="addressRegion">')[1].split("<")[0]
                zc = addinfo.split('itemprop="postalCode">')[1].split("<")[0]
            if 'itemprop="telephone" id="phone-main">' in line2:
                phone = line2.split('itemprop="telephone" id="phone-main">')[1].split(
                    "<"
                )[0]
            if 'itemprop="openingHours" content="' in line2:
                days = line2.split('itemprop="openingHours" content="')
                for day in days:
                    if '<td class="c-hours-details-row-' in day:
                        hrs = day.split('"')[0]
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
        name = name.replace("&#39;", "'")
        add = add.replace("&#39;", "'")
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
    locs = []
    url = "https://www.stuartweitzman.com/stores/index.html"
    r = session.get(url, headers=headers)
    website = "stuartweitzman.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    states = []
    cities = []
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<a class="Directory-listLink" href="' in line:
            items = line.split('<a class="Directory-listLink" href="')
            for item in items:
                if 'data-count="(' in item:
                    count = item.split('data-count="(')[1].split(")")[0]
                    lurl = "https://www.stuartweitzman.com/stores/" + item.split('"')[0]
                    if count == "1":
                        locs.append(lurl)
                    else:
                        states.append(lurl)
    for state in states:
        r2 = session.get(state, headers=headers)
        logger.info(state)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<a class="Directory-listLink" href="' in line2:
                items = line2.split('<a class="Directory-listLink" href="')
                for item in items:
                    if 'data-count="(' in item:
                        count = item.split('data-count="(')[1].split(")")[0]
                        if count == "1":
                            locs.append(
                                "https://www.stuartweitzman.com/stores/"
                                + item.split('"')[0]
                            )
                        else:
                            cities.append(
                                "https://www.stuartweitzman.com/stores/"
                                + item.split('"')[0]
                            )
            if '<a data-ya-track="visitpage" href="../' in line2:
                items = line2.split('<a data-ya-track="visitpage" href="../')
                for item in items:
                    if "Explore This Shop</a>" in item:
                        locs.append(
                            "https://www.stuartweitzman.com/stores/"
                            + item.split('"')[0]
                        )
    for city in cities:
        r2 = session.get(city, headers=headers)
        logger.info(city)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<a data-ya-track="visitpage" href="../' in line2:
                items = line2.split('<a data-ya-track="visitpage" href="../')
                for item in items:
                    if "Explore This Shop</a>" in item:
                        locs.append(
                            "https://www.stuartweitzman.com/stores/"
                            + item.split('"')[0]
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
            if 'geo Heading--lead">' in line2:
                name = line2.split('geo Heading--lead">')[1].split("<")[0]
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[
                    0
                ]
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[
                    0
                ]
            if '<span class="c-address-street-1">' in line2 and add == "":
                addinfo = line2.split('<span class="c-address-street-1">')[1].split(
                    'itemprop="addressCountry">'
                )[0]
                add = addinfo.split("<")[0]
                try:
                    add = (
                        add
                        + " "
                        + addinfo.split('<span class="c-address-street-2">')[1].split(
                            "<"
                        )[0]
                    )
                except:
                    pass
                city = addinfo.split('address-city">')[1].split("<")[0]
                state = addinfo.split('itemprop="addressRegion">')[1].split("<")[0]
                zc = addinfo.split('itemprop="postalCode">')[1].split("<")[0]
            if 'itemprop="telephone" id="phone-main">' in line2:
                phone = line2.split('itemprop="telephone" id="phone-main">')[1].split(
                    "<"
                )[0]
            if 'itemprop="openingHours" content="' in line2:
                days = line2.split('itemprop="openingHours" content="')
                for day in days:
                    if '<td class="c-hours-details-row-' in day:
                        hrs = day.split('"')[0]
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
        name = name.replace("&#39;", "'")
        add = add.replace("&#39;", "'")
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
