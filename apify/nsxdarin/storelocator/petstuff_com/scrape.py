import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("petstuff_com")


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
    alllocs = []
    url = "https://petstuff.com/store-locator"
    r = session.get(url, headers=headers)
    website = "petstuff.com"
    typ = "<MISSING>"
    country = "US"
    Found = False
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "</a><li><a href=/" in line:
            items = line.split("</a><li><a href=/")
            for item in items:
                if "<html>" not in item:
                    lurl = item.split(" ")[0]
                    if "-" in lurl:
                        if "shipping" in lurl:
                            Found = True
                        if lurl not in alllocs and Found is False:
                            alllocs.append(lurl)
                            locs.append("https://petstuff.com/" + lurl)
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
            if "| Petstuff.com|" in line2:
                name = line2.split("| Petstuff.com|")[1].split("<")[0]
            if "ADDRESS:</strong></span><p><span style=font-size:12pt>" in line2:
                add = line2.split(
                    "ADDRESS:</strong></span><p><span style=font-size:12pt>"
                )[1].split("<")[0]
                addinfo = (
                    line2.split(
                        "ADDRESS:</strong></span><p><span style=font-size:12pt>"
                    )[1]
                    .split("</span><p><span style=font-size:12pt>")[1]
                    .split("<")[0]
                )
                city = addinfo.split(",")[0]
                zc = addinfo.rsplit(" ", 1)[1]
                state = addinfo.split(",")[1].strip().split(" ")[0]
            if "PHONE:</strong>" in line2:
                phone = line2.split("PHONE:</strong>")[1].split("<")[0].strip()
            if "data-shoplatitude" in line2:
                lat = line2.split("data-shoplatitude=")[1].split(" ")[0]
                lng = line2.split("data-shoplongitude=")[1].split(" ")[0]
            if "HOURS:</strong></span><p><span style=font-size:12pt>" in line2:
                hours = line2.split(
                    "HOURS:</strong></span><p><span style=font-size:12pt>"
                )[1].split("</span><p><span style=font-size:12pt><strong>")[0]
                hours = hours.replace("</span><p><span style=font-size:12pt>", "; ")
        if "ga-whitemarsh" in loc:
            add = "4717 Highway 80 East"
            city = "Savannah"
            state = "GA"
            zc = "31410"
            hours = (
                "Monday - Friday: 10am - 8pm; Saturday: 10am - 6pm; Sunday: 10am - 6pm"
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
