import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("staybridge_com")

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
    states = []
    alllocs = []
    cities = []
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
            if (
                '"@type":"Hotel","' in line
                and "https://www.ihg.com/staybridge/hotels/" in line
            ):
                lurl = line.split('"url":"')[1].split('"')[0]
                if lurl not in alllocs:
                    alllocs.append(lurl)
                    website = "staybridge.com"
                    typ = "Hotel"
                    hours = "<MISSING>"
                    name = line.split('"name":"')[1].split('"')[0]
                    add = line.split('"streetAddress":"')[1].split('"')[0]
                    city = line.split('"addressLocality":"')[1].split('"')[0]
                    try:
                        state = line.split('"addressRegion":"')[1].split('"')[0]
                    except:
                        state = "<MISSING>"
                    zc = line.split('"postalCode":"')[1].split('"')[0]
                    try:
                        country = line.split('"addressCountry": "')[1].split('"')[0]
                    except:
                        country = "<MISSING>"
                    try:
                        phone = line.split('"telephone":"')[1].split('"')[0]
                    except:
                        phone = "<MISSING>"
                    lat = line.split(',"latitude":')[1].split(",")[0]
                    lng = line.split('"longitude":')[1].split("}")[0]
                    store = lurl.replace("/hoteldetail", "").rsplit("/", 1)[1]
                    yield [
                        website,
                        lurl,
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
    for city in cities:
        try:
            logger.info(("Pulling City %s..." % city))
            r3 = session.get(city, headers=headers)
            if r3.encoding is None:
                r3.encoding = "utf-8"
            for line3 in r3.iter_lines(decode_unicode=True):
                if (
                    "https://www.ihg.com/staybridge/hotels/" in line3
                    and '{"@context":"https://www.schema.org"' in line3
                ):
                    lurl = line3.split('"url":"')[1].split('"')[0]
                    if lurl not in alllocs:
                        alllocs.append(lurl)
                        website = "staybridge.com"
                        typ = "Hotel"
                        hours = "<MISSING>"
                        name = line3.split('"name":"')[1].split('"')[0]
                        add = line3.split('"streetAddress":"')[1].split('"')[0]
                        city = line3.split('"addressLocality":"')[1].split('"')[0]
                        try:
                            state = line3.split('"addressRegion":"')[1].split('"')[0]
                        except:
                            state = "<MISSING>"
                        zc = line3.split('"postalCode":"')[1].split('"')[0]
                        if "canada" in url:
                            country = "CA"
                        else:
                            country = "US"
                        try:
                            phone = line3.split('"telephone":"')[1].split('"')[0]
                        except:
                            phone = "<MISSING>"
                        lat = line3.split(',"latitude":')[1].split(",")[0]
                        lng = line3.split('"longitude":')[1].split("}")[0]
                        store = lurl.replace("/hoteldetail", "").rsplit("/", 1)[1]
                        yield [
                            website,
                            lurl,
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
        except:
            pass


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
