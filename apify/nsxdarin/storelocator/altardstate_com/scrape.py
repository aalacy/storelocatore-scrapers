import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("altardstate_com")


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
    url = "https://www.altardstate.com/on/demandware.store/Sites-altardstate-Site/default/Stores-FindStores?showMap=true&radius=5000&postalCode=55441&radius=300"
    r = session.get(url, headers=headers)
    website = "altardstate.com"
    typ = "<MISSING>"
    loc = "<MISSING>"
    country = "US"
    Found = False
    name = ""
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '\\"isABSStore\\":' in line:
            items = line.split('\\"isABSStore\\":')
            for item in items:
                if '\\"name\\":\\"' in item:
                    name = item.split('\\"name\\":\\"')[1].split('\\",')[0]
                    lat = item.split('"latitude\\":')[1].split(",")[0]
                    lng = item.split('"longitude\\":')[1].split(",")[0]
                    store = item.split('data-store-id=\\\\\\"')[1].split("\\")[0]
                    add = (
                        item.split(
                            '<div class=\\\\\\"store-name store-locator-store-addr\\\\\\">\\\\n'
                        )[1]
                        .split("\\\\n")[0]
                        .strip()
                        .replace("\t", "")
                    )
                    city = item.split(
                        '<div class=\\\\\\"store-name store-locator-store-addr\\\\\\">\\\\n'
                    )[2].split(",")[0]
                    state = (
                        item.split(
                            '<div class=\\\\\\"store-name store-locator-store-addr\\\\\\">\\\\n'
                        )[2]
                        .split("\\\\n                        \\\\n")[1]
                        .split("<")[0]
                        .strip()
                        .replace("\t", "")
                    )
                    zc = item.split("<span> </span>")[1].split("\\")[0]
                    phone = item.split('storelocator-phone\\\\\\" href=\\\\\\"tel:')[
                        1
                    ].split("\\")[0]
                    hours = (
                        item.split('=\\\\\\"store-locator-hours-text\\\\\\">')[1]
                        .split("</span>")[0]
                        .replace("<br />\\\\n", "; ")
                    )
                    hours = hours.rsplit("</p>\\\\n\\\\n<p>", 1)[1]
                    city = city.strip().replace("\t", "")
                    if '\\"">' in hours:
                        hours = hours.rsplit('\\\\\\"">', 1)[1]
                    hours = (
                        hours.replace("\\\\n", "")
                        .replace("<p>", "")
                        .replace("</p>", "")
                    )
                    if '"">' in hours:
                        hours = hours.rsplit('"">', 1)[1]
                    if "margin" in hours:
                        hours = "<MISSING>"
                    if "BRIDGE STREET" in name:
                        hours = "Sun: Noon-6PM; Mon-Sat: 11AM-7PM"
                    if "WEST TOWN MALL" in name:
                        hours = "Sun-Thu: 11AM-7PM; Fri-Sat: 11AM-8PM"
                    if "THE PINNACLE AT TURKEY CREEK" in name:
                        hours = "Sun: Noon-6PM; Mon-Sat: 11AM-7PM"
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
