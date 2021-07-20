import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("victoriassecret_co_uk")


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
    url = "https://www.victoriassecret.co.uk/store-locator"
    r = session.get(url, headers=headers)
    website = "victoriassecret.co.uk"
    typ = "<MISSING>"
    country = "GB"
    loc = "<MISSING>"
    store = "<MISSING>"
    hours = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<button class="vs-store-btn">' in line:
            items = line.split('<button class="vs-store-btn">')
            for item in items:
                if '<div class="vs-store-address">' in item:
                    name = item.split("<strong>")[1].split("<")[0]
                    phone = (
                        item.split('<div class="vs-store-address">')[1]
                        .split("<strong>")[1]
                        .split("<")[0]
                    )
                    addinfo = item.split('<div class="vs-store-address">')[1].split(
                        "<br><br> <strong>"
                    )[0]
                    zc = addinfo.rsplit(">", 1)[1].strip()
                    state = "<MISSING>"
                    add = addinfo.rsplit("<br>", 2)[0].strip().replace("<br>", "")
                    city = addinfo.rsplit("<br>", 2)[1].strip()
                    if "Upper Level 3 Birmingham" in add:
                        city = "Birmingham"
                        add = add.split(" Birmingham")[0].strip()
                    if "Glasgow" in add:
                        add = add.split("Glasgow")[0].strip()
                        city = "Glasgow"
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
