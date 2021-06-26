import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("avidhotels_com")

session = SgRequests()
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


def fetch_data():
    states = []
    cities = []
    locs = []
    url_home = "https://www.ihg.com/destinations/us/en/explore"
    r = session.get(url_home, headers=headers)
    Found = False
    cities = []
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '-hotels"><span>' in line:
            if (
                'href="https://www.ihg.com/destinations/us/en/mexico/' in line
                or 'href="https://www.ihg.com/destinations/us/en/canada/' in line
                or 'href="https://www.ihg.com/destinations/us/en/united-states/' in line
            ):
                lurl = line.split('href="')[1].split('"')[0]
                if lurl not in states:
                    states.append(lurl)
        if 'algeria-hotels">' in line:
            Found = True
        if (
            Found
            and '-hotels"><span>' in line
            and "united-states/" not in line
            and "/mexico/" not in line
            and "/canada/" not in line
        ):
            lurl = line.split('href="')[1].split('"')[0]
            if lurl not in states:
                states.append(lurl)
    for url in states:
        logger.info(url)
        r = session.get(url, headers=headers)
        lines = r.iter_lines()
        for line in lines:
            line = str(line.decode("utf-8"))
            if '<li class="listingItem"><a' in line:
                g = next(lines)
                g = str(g.decode("utf-8"))
                if 'href="' not in g:
                    g = next(lines)
                    g = str(g.decode("utf-8"))
                curl = g.split('href="')[1].split('"')[0]
                if curl not in cities:
                    cities.append(curl)
            if '"@type":"Hotel","' in line:
                curl = (
                    line.split('"@type":"Hotel","')[1].split('"url":"')[1].split('"')[0]
                )
                if curl not in locs:
                    if "avidhotels" in curl:
                        locs.append(curl)
    for url in cities:
        try:
            logger.info(url)
            r = session.get(url, headers=headers)
            lines = r.iter_lines()
            for line in lines:
                line = str(line.decode("utf-8"))
                if '"@type":"Hotel","' in line:
                    curl = (
                        line.split('"@type":"Hotel","')[1]
                        .split('"url":"')[1]
                        .split('"')[0]
                    )
                    if curl not in locs:
                        if "avidhotels" in curl:
                            locs.append(curl)
        except:
            pass
    for loc in locs:
        logger.info(loc)
        r2 = session.get(loc, headers=headers)
        website = "avidhotels.com"
        name = ""
        city = ""
        state = ""
        country = "US"
        add = ""
        zc = ""
        typ = "Hotel"
        phone = ""
        hours = "<MISSING>"
        lat = ""
        lng = ""
        add2 = ""
        city2 = ""
        zc2 = ""
        state2 = ""
        phone2 = ""
        country2 = ""
        lat2 = ""
        lng2 = ""
        store = loc.split("/hoteldetail")[0].rsplit("/", 1)[1]
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'value="MXN"' in line2:
                country = "MX"
            if 'property="og:title" content="' in line2 and name == "":
                name = line2.split('property="og:title" content="')[1].split('"')[0]
            if '"name" : "' in line2 and name == "":
                name = line2.split('"name" : "')[1].split('"')[0]
            if '"streetAddress": "' in line2 and add == "":
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if '<span itemprop="streetAddress">' in line2 and add == "":
                add = (
                    line2.split('<span itemprop="streetAddress">')[1]
                    .split("</span>")[0]
                    .strip()
                    .replace("<p>", "")
                    .replace("</p>", "")
                    .strip()
                )
                city = (
                    line2.split('<span itemprop="addressLocality">')[1]
                    .split("<")[0]
                    .strip()
                )
                state = line2.split('<span itemprop="addressRegion">')[1].split("<")[0]
                zc = line2.split('<span itemprop="postalCode">')[1].split("<")[0]
            if '"addressLocality": "' in line2 and city == "":
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if lat == "" and '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[
                    0
                ]
            if lng == "" and '<meta itemprop="longitude" content="' in line2:
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[
                    0
                ]
            if '"addressRegion": "' in line2 and state == "":
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if phone == "" and 'itemprop="telephone">' in line2:
                phone = line2.split('itemprop="telephone">')[1].split("<")[0]
            if '"addressCountry": "' in line2 and country == "":
                country = line2.split('"addressCountry": "')[1].split('"')[0]
            if '"latitude": "' in line2 and lat == "":
                lat = line2.split('"latitude": "')[1].split('"')[0]
            if '"longitude": "' in line2 and lng == "":
                lng = line2.split('"longitude": "')[1].split('"')[0]
            if '"telephone": "' in line2 and phone == "":
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if 'itemprop="streetAddress">' in line2:
                add2 = line2.split('itemprop="streetAddress">')[1].split("<")[0]
            if 'itemprop="addressRegion">' in line2:
                state2 = line2.split('itemprop="addressRegion">')[1].split("<")[0]
            if 'itemprop="addressLocality">' in line2:
                city2 = line2.split('itemprop="addressLocality">')[1].split("<")[0]
            if 'itemprop="postalCode">' in line2:
                zc2 = line2.split('itemprop="postalCode">')[1].split("<")[0]
            if '<meta itemprop="latitude" content="' in line2:
                lat2 = line2.split('<meta itemprop="latitude" content="')[1].split('"')[
                    0
                ]
            if '<meta itemprop="longitude" content="' in line2:
                lng2 = line2.split('<meta itemprop="longitude" content="')[1].split(
                    '"'
                )[0]
            if 'itemprop="telephone">' in line2:
                phone2 = line2.split('itemprop="telephone">')[1].split("<")[0]
            if 'itemprop="addressCountry">' in line2:
                country2 = line2.split('itemprop="addressCountry">')[1].split("<")[0]
        if add == "":
            add = add2
        if city == "":
            city = city2
        if state == "":
            state = state2
        if zc == "":
            zc = zc2
        if lat == "":
            lat = lat2
        if lng == "":
            lng = lng2
        if country == "":
            country = country2
        if phone == "":
            phone = phone2
        if "null" in phone or phone == "":
            phone = "<MISSING>"
        if state == "":
            state = "<MISSING>"
        if add == "":
            add = "<MISSING>"
        if lat == "":
            lat = "<MISSING>"
        if lng == "":
            lng = "<MISSING>"
        if zc == "":
            zc = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if city == "":
            city = "<MISSING>"
        state = state.replace("&nbsp;", "")
        city = city.replace("&nbsp;", "")
        if " Hotels" not in name and name != "":
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
