import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("platt_com")


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
    url = "https://platt.com/StoreLocator.aspx"
    r = session.get(url, headers=headers)
    website = "platt.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<li><a href='" in line:
            lurl = "https://platt.com/" + line.split("<li><a href='")[1].split("'")[0]
            if lurl not in locs:
                locs.append(lurl)
    for loc in locs:
        logger.info(loc)
        add = ""
        store = loc.split("id=")[1]
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                g = next(lines)
                g = str(g.decode("utf-8"))
                name = g.replace("\r", "").replace("\n", "").replace("\t", "").strip()
                name = name.replace(" - Platt Electric Supply", "")
            if "var markerstore = [" in line2:
                g = next(lines)
                g = str(g.decode("utf-8"))
                lat = g.split('", "')[1]
                lng = g.split('", "')[2]
                add = g.split('", "')[3]
                city = g.split('", "')[4]
                state = g.split('", "')[5]
                zc = g.split('", "')[6]
                phone = g.split('", "')[7]
                hours = g.split('", "')[8]
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
