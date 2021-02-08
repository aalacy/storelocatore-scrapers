import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("wendys_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "authority": "locationservices.wendys.com",
    "scheme": "https",
    "method": "GET",
    "cache-control": "max-age=0",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
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
    urls = [
        "https://locations.wendys.com/united-states",
        "https://locations.wendys.com/canada",
    ]
    locs = []
    alllocs = []
    states = []
    cities = []
    for url in urls:
        if "united-states" in url:
            country = "US"
        else:
            country = "CA"
        r = session.get(url, headers=headers)
        if r.encoding is None:
            r.encoding = "utf-8"
        for line in r.iter_lines(decode_unicode=True):
            if '<a class="Directory-listLink" href="' in line:
                items = line.split('<a class="Directory-listLink" href="')
                for item in items:
                    if 'Directory-listLinkCount">(' in item:
                        count = item.split('Directory-listLinkCount">(')[1].split(")")[
                            0
                        ]
                        lurl = "https://locations.wendys.com/" + item.split('"')[0]
                        lurl = lurl.replace("&#39;", "'").replace("&amp;", "&")
                        if count == "1":
                            locs.append(lurl)
                        else:
                            states.append(lurl)
        for state in states:
            logger.info("Pulling State %s..." % state)
            r2 = session.get(state, headers=headers)
            if r2.encoding is None:
                r2.encoding = "utf-8"
            for line2 in r2.iter_lines(decode_unicode=True):
                if '<a class="Directory-listLink" href="..' in line2:
                    items = line2.split('<a class="Directory-listLink" href="..')
                    for item in items:
                        if ' class="Directory-listLinkCount">(' in item:
                            count = item.split(' class="Directory-listLinkCount">(')[
                                1
                            ].split(")")[0]
                            lurl = "https://locations.wendys.com" + item.split('"')[0]
                            lurl = lurl.replace("&#39;", "'").replace("&amp;", "&")
                            if count == "1":
                                locs.append(lurl)
                            else:
                                cities.append(lurl)
        for city in cities:
            logger.info(city)
            r2 = session.get(city, headers=headers)
            if r2.encoding is None:
                r2.encoding = "utf-8"
            for line2 in r2.iter_lines(decode_unicode=True):
                if 'data-ya-track="visitpage" href="../../' in line2:
                    items = line2.split('data-ya-track="visitpage" href="../../')
                    for item in items:
                        if "Visit Store Page</a>" in item:
                            lurl = "https://locations.wendys.com/" + item.split('"')[0]
                            lurl = lurl.replace("&#39;", "'").replace("&amp;", "&")
                            locs.append(lurl)
        for loc in locs:
            loc = loc.replace("&#39;", "'")
            logger.info(loc)
            Closed = False
            website = "wendys.com"
            typ = "Restaurant"
            name = ""
            phone = ""
            add = ""
            city = ""
            state = ""
            zc = ""
            lat = ""
            lng = ""
            hours = ""
            store = "<MISSING>"
            r2 = session.get(loc, headers=headers)
            if r2.encoding is None:
                r2.encoding = "utf-8"
            for line2 in r2.iter_lines(decode_unicode=True):
                if 'itemprop="name">' in line2 and name == "":
                    name = line2.split('itemprop="name">')[1].split("<")[0]
                if "'dimension4', '" in line2:
                    add = line2.split("'dimension4', '")[1].split("'")[0]
                    city = line2.split("'dimension3', '")[1].split("'")[0]
                    state = line2.split("'dimension2', '")[1].split("'")[0]
                    zc = line2.split("'dimension5', '")[1].split("'")[0]
                if phone == "" and 'c-phone-main-number-link" href="tel:+' in line2:
                    phone = line2.split('c-phone-main-number-link" href="tel:+')[
                        1
                    ].split('"')[0]
                if '<meta itemprop="latitude" content="' in line2:
                    lat = line2.split('<meta itemprop="latitude" content="')[1].split(
                        '"'
                    )[0]
                    lng = line2.split('<meta itemprop="longitude" content="')[1].split(
                        '"'
                    )[0]
                if hours == "" and "Restaurant Hours</h4>" in line2:
                    days = (
                        line2.split("Restaurant Hours</h4>")[1]
                        .split("data-days='[{")[1]
                        .split("}]'")[0]
                        .split('"day":"')
                    )
                    for day in days:
                        if '"intervals"' in day:
                            if (
                                '"intervals":[]' not in day
                                and '"intervals":null' not in day
                            ):
                                hrs = (
                                    day.split('"')[0]
                                    + ": "
                                    + day.split(',"start":')[1].split("}")[0]
                                    + "-"
                                    + day.split('"end":')[1].split(",")[0]
                                )
                            else:
                                hrs = day.split('"')[0] + ": Closed"
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
            if hours == "":
                hours = "<MISSING>"
            if phone == "":
                phone = "<MISSING>"
            infotext = name + "|" + add + "|" + city
            if infotext not in alllocs and Closed is False and add != "":
                alllocs.append(infotext)
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
