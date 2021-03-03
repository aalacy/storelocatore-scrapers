import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("1909tavernemoderne_com")


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
    url = "https://1909tavernemoderne.com"
    r = session.get(url, headers=headers)
    website = "1909tavernemoderne.com"
    typ = "<MISSING>"
    country = "CA"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<h2 style="font-size:' in line:
            locs.append(line.split('href="')[1].split('"')[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = "<MISSING>"
        lat = "<MISSING>"
        lng = "<MISSING>"
        hours = "<MISSING>"
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                name = line2.split("<title>")[1].split("&")[0].strip()
            if '<p><span style="color: #000000;">' in line2:
                add = line2.split('<p><span style="color: #000000;">')[1].split("<")[0]
                g = next(lines)
                g = str(g.decode("utf-8"))
                city = g.split("(")[0].strip().split(">")[1]
                state = g.split("(")[1].split(")")[0]
                zc = g.split(")")[1].strip().split("<")[0]
        if "laval" in loc:
            add = "1950, Rue Claude-Gagne"
            city = "Laval"
            state = "Quebec"
            zc = "H7N5H9"
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
