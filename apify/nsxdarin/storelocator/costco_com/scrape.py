import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from tenacity import retry, stop_after_attempt

logger = SgLogSetup().get_logger("costco_com")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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


@retry(stop=stop_after_attempt(7))
def fetch_loc(loc):
    session = SgRequests()
    return session.get(loc, headers=headers)


def fetch_data():
    locs = []
    url = "https://www.costco.com/sitemap_l_001.xml"
    r = fetch_loc(url)
    for raw_line in r.iter_lines():
        line = str(raw_line)
        if "<loc>https://www.costco.com/warehouse-locations/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
    for loc in locs:
        logger.info(loc)
        website = "costco.com"
        name = "<MISSING>"
        typ = "Warehouse"
        hours = ""
        phone = ""
        add = ""
        city = ""
        zc = ""
        state = ""
        lat = ""
        lng = ""
        store = ""
        country = "US"
        HFound = False
        r2 = fetch_loc(loc)
        for raw_line2 in r2.iter_lines():
            line2 = str(raw_line2)
            if 'col-sm-6 hours">' in line2:
                HFound = True
            if HFound and "</div>" in line2:
                HFound = False
            if HFound and 'itemprop="openingHours" datetime="' in line2:
                hrs = line2.split('itemprop="openingHours" datetime="')[1].split('"')[0]
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if 'itemprop="latitude" content="' in line2:
                lat = line2.split('itemprop="latitude" content="')[1].split('"')[0]
            if 'itemprop="longitude" content="' in line2:
                lng = line2.split('itemprop="longitude" content="')[1].split('"')[0]
            if 'data-identifier="' in line2:
                store = line2.split('data-identifier="')[1].split('"')[0]
            if "<h1" in line2:
                name = (
                    line2.split("<h1")[1]
                    .split(">")[1]
                    .split("<")[0]
                    .replace("&nbsp;", " ")
                )
            if 'itemprop="streetAddress">' in line2:
                add = line2.split('itemprop="streetAddress">')[1].split("<")[0]
            if 'itemprop="addressLocality">' in line2:
                city = line2.split('itemprop="addressLocality">')[1].split("<")[0]
            if 'itemprop="addressRegion">' in line2:
                state = line2.split('itemprop="addressRegion">')[1].split("<")[0]
            if 'itemprop="postalCode">' in line2:
                zc = line2.split('itemprop="postalCode">')[1].split("<")[0]
            if phone == "" and 'itemprop="telephone">' in line2:
                phone = (
                    line2.split('itemprop="telephone">')[1]
                    .split("<")[0]
                    .strip()
                    .replace("\t", "")
                )
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if add != "":
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

    countries = []
    session = SgRequests()
    url = "https://www.costco.com"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<div><a href="https://www.costco.' in line and ".uk" not in line:
            countries.append(
                line.split('href="')[1].split('"')[0] + "/store-finder/search?q=&page=0"
            )
    for co in countries:
        logger.info(co)
        website = "costco.com"
        name = "<MISSING>"
        typ = "Warehouse"
        dc = 0
        country = co.split("/store-")[0].rsplit(".", 1)[1].upper()
        if country == "UK":
            country = "GB"
        r2 = session.get(co, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        lines = r2.iter_lines(decode_unicode=True)
        for line2 in lines:
            if '"displayName" : "' in line2:
                hours = ""
                phone = ""
                add = ""
                city = ""
                zc = ""
                state = ""
                lat = ""
                loc = ""
                lng = ""
                store = "<MISSING>"
                dc = 0
                name = line2.split('"displayName" : "')[1].split('"')[0]
            if '"url" : "' in line2:
                loc = co.split("/store-")[0] + line2.split('"url" : "')[1].split('"')[
                    0
                ].replace("\\", "")
            if '"phone" : "' in line2:
                phone = line2.split('"phone" : "')[1].split('"')[0]
            if '"line1" : "' in line2:
                add = line2.split('"line1" : "')[1].split('"')[0]
            if '"line2" : "' in line2:
                add = add + " " + line2.split('"line2" : "')[1].split('"')[0]
                add = add.strip()
            if '"town" : "' in line2:
                city = line2.split('"town" : "')[1].split('"')[0]
                state = "<MISSING>"
            if '"postalCode"' in line2:
                zc = line2.split('"postalCode" : "')[1].split('"')[0]
            if '"latitude" : "' in line2:
                lat = line2.split('"latitude" : "')[1].split('"')[0]
            if '"longitude"' in line2:
                lng = line2.split('"longitude" : "')[1].split('"')[0]
            if ':{"individual":' in line2:
                day = line2.split('"')[1]
                dc = dc + 1
                g = next(lines)
                g = next(lines)
                hrs = day + ": " + g.split('"')[1]
                if dc <= 7:
                    if hours == "":
                        hours = hrs
                    else:
                        hours = hours + "; " + hrs
            if '"image"' in line2:
                if city == "":
                    city = "<MISSING>"
                if hours == "":
                    hours = "<MISSING>"
                if "?" in loc:
                    loc = loc.split("?")[0]
                if phone == "":
                    phone = "<MISSING>"
                if zc == "":
                    zc = "<MISSING>"
                if state == "":
                    state = "<MISSING>"
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
