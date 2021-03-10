import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("bigy_com")


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
    for x in range(1, 130):
        url = "https://www.bigy.com/rs/storelocator/detail/" + str(x)
        r = session.get(url, headers=headers)
        website = "bigy.com"
        typ = "<MISSING>"
        country = "US"
        loc = url
        store = str(x)
        logger.info("Pulling Store #%s..." % str(x))
        lines = r.iter_lines()
        for line in lines:
            line = str(line.decode("utf-8"))
            if 'property="name">' in line:
                name = (
                    line.split('property="name">')[1]
                    .split("<")[0]
                    .replace("&nbsp;", " ")
                )
            if '"PostalAddress">' in line:
                add = line.split('"PostalAddress">')[1].split("<")[0]
                g = next(lines)
                g = str(g.decode("utf-8"))
                addinfo = g.strip().replace("\t", "").split("<")[0]
                city = addinfo.split(",")[0]
                state = addinfo.split(",")[1].strip().split(" ")[0]
                zc = addinfo.rsplit(" ", 1)[1]
            if '"telephone" content="' in line:
                phone = line.split('"telephone" content="')[1].split('"')[0]
            if '"openingHours" content="' in line:
                hours = (
                    line.split('"openingHours" content="')[1]
                    .split(">")[1]
                    .split("<")[0]
                )
            if ".storeDetail.initMap('" in line:
                lat = line.split(".storeDetail.initMap('")[1].split("'")[0]
                lng = (
                    line.split(".storeDetail.initMap('")[1]
                    .split(", '")[1]
                    .split("'")[0]
                )
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
