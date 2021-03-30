import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger(
    "nhs_uk__ServiceDirectories__Pages__NHSTrustListing_aspx"
)


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
    typ = "<MISSING>"
    country = "GB"
    website = "nhs.uk/ServiceDirectories/Pages/NHSTrustListing_aspx"
    for x in range(1, 140):
        url = (
            "https://www.nhs.uk/service-search/other-services/Hospital/Low-Catton/Results/3/-0.925/53.977/7/13314?distance=10000&ResultsOnPageValue=10&isNational=0&totalItems=1219&currentPage="
            + str(x)
        )
        r = session.get(url, headers=headers)
        logger.info("Pulling Page %s..." % str(x))
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '<a href="/Services/hospitals/Overview/DefaultView.aspx?id=' in line:
                locs.append(
                    "https://www.nhs.uk" + line.split('href="')[1].split('"')[0]
                )
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = "<MISSING>"
        zc = ""
        store = loc.split("id=")[1]
        phone = ""
        lat = "<MISSING>"
        lng = "<MISSING>"
        hours = "<MISSING>"
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<h1 property="name"' in line2:
                name = line2.split('<h1 property="name"')[1].split(">")[1].split("<")[0]
            if 'property="telephone">' in line2:
                phone = line2.split('property="telephone">')[1].split("<")[0]
            if '"streetAddress">' in line2:
                add = line2.split('"streetAddress">')[1].split("<")[0]
            if '"addressLocality">' in line2:
                city = line2.split('"addressLocality">')[1].split("<")[0]
                try:
                    state = line2.split('property="addressRegion">')[1].split("<")[0]
                except:
                    state = "<MISSING>"
                zc = line2.split('="postalCode">')[1].split("<")[0]
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
