import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("cherryberryyogurtbar_com")


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
    for x in range(0, 5):
        url = "https://www.cherryberryyogurtbar.com/find-a-location?page=" + str(x)
        r = session.get(url, headers=headers)
        website = "cherryberryyogurtbar.com"
        typ = "<MISSING>"
        country = "US"
        loc = "<MISSING>"
        name = "Cherry Berry"
        logger.info("Pulling Stores")
        lines = r.iter_lines()
        for line in lines:
            line = str(line.decode("utf-8"))
            if '<span itemprop="streetAddress">' in line:
                phone = "<MISSING>"
                city = ""
                state = ""
                zc = ""
                lat = ""
                lng = ""
                country = "US"
                add = (
                    line.split('<span itemprop="streetAddress">')[1]
                    .split("<")[0]
                    .strip()
                )
            if 'itemprop="addressLocality">' in line:
                city = line.split('itemprop="addressLocality">')[1].split("<")[0]
                state = line.split('addressRegion">')[1].split("<")[0]
            if 'itemprop="postalCode">' in line:
                zc = line.split('itemprop="postalCode">')[1].split("<")[0]
                store = "<MISSING>"
            if 'data-lat="' in line:
                lat = line.split('data-lat="')[1].split('"')[0]
                lng = line.split('long="')[1].split('"')[0]
            if '<a href="tel:' in line:
                phone = line.split('">')[1].split("<")[0]
            if (
                '<td  class="views-field views-field-field-catering hidden-xs" >'
                in line
            ):
                hours = "<MISSING>"
                if " " in zc:
                    country = "CA"
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
