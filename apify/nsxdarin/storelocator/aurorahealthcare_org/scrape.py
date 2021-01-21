import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("aurorahealthcare_org")


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
    url = "https://www.aurorahealthcare.org/sitemap.xml"
    r = session.get(url, headers=headers)
    website = "aurorahealthcare.org"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://www.aurorahealthcare.org/locations/" in line:
            items = line.split("<loc>https://www.aurorahealthcare.org/locations/")
            for item in items:
                if "xmlns" not in item:
                    locs.append(
                        "https://www.aurorahealthcare.org/locations/"
                        + item.split("<")[0]
                    )
    for loc in locs:
        logger.info(loc)
        name = ""
        typ = loc.split("/locations/")[1].split("/")[0]
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
            if "var hoursOfOperation = [" in line2:
                days = line2.split("var hoursOfOperation = [")[1].split('"Day":"')
                for day in days:
                    if '"EndTimes":' in day:
                        hrs = (
                            day.split('"')[0]
                            + ": "
                            + day.split('"StartTimes":["')[1].split('"')[0]
                            + "-"
                            + day.split('"EndTimes":["')[1].split('"')[0]
                        )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
            if "<title>" in line2:
                name = line2.split("<title>")[1].split("<")[0]
                if " |" in name:
                    name = name.split(" |")[0]
            if 'itemprop="streetAddress">' in line2:
                add = line2.split('itemprop="streetAddress">')[1].split("<")[0]
            if '<span itemprop="addressLocality">' in line2:
                city = line2.split('<span itemprop="addressLocality">')[1].split("<")[0]
            if 'itemprop="addressRegion">' in line2:
                state = line2.split('itemprop="addressRegion">')[1].split("<")[0]
            if 'itemprop="postalCode">' in line2:
                zc = line2.split('itemprop="postalCode">')[1].split("<")[0]
            if phone == "" and '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
            if 'data-latitude="' in line2:
                lat = line2.split('data-latitude="')[1].split('"')[0]
                lng = line2.split('longitude="')[1].split('"')[0]
        if hours == "":
            hours = "<MISSING>"
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


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
