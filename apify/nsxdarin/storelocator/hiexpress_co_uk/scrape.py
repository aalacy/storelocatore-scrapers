import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("hiexpress_co_uk")


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
    ids = []
    states = []
    url = (
        "https://www.ihg.com/holidayinnexpress/destinations/gb/en/united-kingdom-hotels"
    )
    r = session.get(url, headers=headers)
    website = "hiexpress.co.uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "hotels</span></a>" in line:
            sname = line.split('href="')[1].split('"')[0]
            if sname not in states:
                states.append(sname)
    for state in states:
        logger.info(state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if ',"name":"Holiday Inn Express ' in line2:
                locs.append(line2.split('"url":"')[1].split('"')[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = loc.split("/hoteldetail")[0].rsplit("/", 1)[1]
        phone = ""
        lat = ""
        lng = ""
        hours = "<MISSING>"
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '"og:title" content="' in line2 and name == "":
                name = line2.split('"og:title" content="')[1].split('"')[0]
            if 'location:latitude"  content="' in line2:
                lat = line2.split('location:latitude"  content="')[1].split('"')[0]
            if 'location:longitude" content="' in line2:
                lng = line2.split('location:longitude" content="')[1].split('"')[0]
            if 'itemprop="streetAddress">' in line2:
                add = line2.split('itemprop="streetAddress">')[1].split("<")[0]
            if 'itemprop="addressLocality">' in line2:
                city = (
                    line2.split('itemprop="addressLocality">')[1]
                    .split("<")[0]
                    .replace(",", "")
                )
            if 'itemprop="postalCode">' in line2:
                zc = line2.split('itemprop="postalCode">')[1].split("<")[0]
                state = "<MISSING>"
            if '<a href="tel:' in line2:
                phone = (
                    line2.split('<a href="tel:')[1]
                    .split('"')[0]
                    .replace("<p>", "")
                    .replace("</p>", "")
                )
        if store not in ids:
            ids.append(store)
            if phone == "":
                phone = "<MISSING>"
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
