import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("ladyfootlocker_com")


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
    url = "https://stores.ladyfootlocker.com/sitemap.xml"
    r = session.get(url, headers=headers)
    website = "ladyfootlocker.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if (
            'rel="alternate" hreflang="en" href="https://stores.ladyfootlocker.com/'
            in line
        ):
            lurl = line.split('href="')[1].split('"')[0]
            if lurl.count("/") == 6 and "-" in lurl.rsplit("/", 1)[1]:
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
            if '<span class="LocationName-geo">' in line2 and name == "":
                name = line2.split('<span class="LocationName-geo">')[1].split("<")[0]
            if '<meta itemprop="addressLocality" content="' in line2:
                city = line2.split('<meta itemprop="addressLocality" content="')[
                    1
                ].split('"')[0]
            if 'itemprop="streetAddress" content="' in line2:
                add = line2.split('itemprop="streetAddress" content="')[1].split('"')[0]
                try:
                    city = line2.split('itemprop="addressLocality">')[1].split("<")[0]
                except:
                    pass
                try:
                    state = line2.split('itemprop="addressRegion">')[1].split("<")[0]
                except:
                    state = "PR"
                zc = line2.split('itemprop="postalCode">')[1].split("<")[0]
            if '<a class="Phone-link" href="tel:' in line2:
                phone = (
                    line2.split('<a class="Phone-link" href="tel:')[1]
                    .split('"')[0]
                    .replace("+1", "")
                )
            if 'itemprop="latitude" content="' in line2:
                lat = line2.split('itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('itemprop="longitude" content="')[1].split('"')[0]
            if "data-days='[{" in line2 and hours == "":
                days = line2.split("data-days='[{")[1].split("]}]")[0].split('"day":"')
                for day in days:
                    if '"start"' in day:
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
        if hours == "":
            hours = "<MISSING>"
        if "elmhurst/90-15-queens-blvd" in loc:
            hours = "Closed"
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
