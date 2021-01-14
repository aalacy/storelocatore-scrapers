import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("topshop_co_uk")


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
    url = "https://stores.topshop.com/index.html"
    r = session.get(url, headers=headers)
    website = "topshop.co.uk"
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
                        locs.append("https://stores.topshop.com/" + item.split('"')[0])
                    else:
                        cities.append(
                            "https://stores.topshop.com/" + item.split('"')[0]
                        )
    for city in cities:
        logger.info(city)
        r2 = session.get(city, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'a data-ya-track="visitpage" href="' in line2:
                items = line2.split('a data-ya-track="visitpage" href="')
                for item in items:
                    if ">Store Details<" in item:
                        locs.append("https://stores.topshop.com/" + item.split('"')[0])
    for loc in locs:
        lurl = loc.replace("&#39;", "'").replace("&amp;", "&")
        logger.info(lurl)
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
        Closed = False
        r2 = session.get(lurl, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "temporarily closed" in line2:
                Closed = True
            if "<title>" in line2:
                if '"geo.region" content="United Kingdom-' in line2:
                    state = (
                        line2.split('"geo.region" content="United Kingdom-')[1]
                        .split('"')[0]
                        .replace("-", " ")
                    )
                if 'name="geo.region" content="Ireland-' in line2:
                    state = (
                        line2.split('name="geo.region" content="Ireland-')[1]
                        .split('"')[0]
                        .replace("-", " ")
                    )
                name = line2.split("<title>")[1].split(" |")[0]
                add = line2.split('"streetAddress" content="')[1].split('"')[0]
                city = line2.split('class="c-address-city">')[1].split("<")[0]
                try:
                    zc = line2.split('temprop="postalCode">')[1].split("<")[0]
                except:
                    zc = "<MISSING>"
                phone = line2.split('id="phone-main">')[1].split("<")[0]
                lat = line2.split('itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('itemprop="longitude" content="')[1].split('"')[0]
                days = line2.split('itemprop="openingHours" content="')
                for day in days:
                    if '<td class="c-hours-details' in day:
                        hrs = day.split('"')[0]
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
        if state == "":
            state = "<MISSING>"
        if Closed:
            hours = "Closed"
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


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
