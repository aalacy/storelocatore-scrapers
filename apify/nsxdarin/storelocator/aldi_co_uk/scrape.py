import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("aldi_co_uk")


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
    url = "https://www.aldi.co.uk/sitemap/store-en_gb-gbp"
    locs = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://www.aldi.co.uk/store/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
    for loc in locs:
        logger.info(loc)
        website = "aldi.co.uk"
        typ = "<MISSING>"
        country = "GB"
        hours = ""
        phone = "<MISSING>"
        name = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '{"name":"' in line2 and name == "":
                name = line2.split('{"name":"')[1].split('"')[0]
                try:
                    hours = (
                        line2.split('"openingHours":["')[1]
                        .split('"]')[0]
                        .replace('","', "; ")
                    )
                except:
                    hours = "<MISSING>"
                city = line2.split('"addressLocality":"')[1].split('"')[0]
                state = "<MISSING>"
                add = line2.split(',"streetAddress":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
            if '"latlng":{"lat":' in line2:
                lat = line2.split('"latlng":{"lat":')[1].split(",")[0]
                lng = line2.split(',"lng":')[1].split("}")[0]
            if '{"code":"s-uk-' in line2:
                store = line2.split('"code":"s-uk-')[1].split('"')[0]
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
