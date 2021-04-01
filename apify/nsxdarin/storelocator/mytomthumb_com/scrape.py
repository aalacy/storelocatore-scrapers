import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("mytomthumb_com")


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
    url = "https://www.mytomthumb.com/wp-admin/admin-ajax.php?action=get_all_stores&lat=&lng="
    r = session.get(url, headers=headers)
    website = "mytomthumb.com"
    typ = "<MISSING>"
    country = "US"
    store = "<MISSING>"
    hours = "Sun-Sat: 24 Hours"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"ID":"' in line:
            items = line.split('"ID":"')
            for item in items:
                if '"na":"' in item:
                    name = item.split('"na":"')[1].split('"')[0]
                    loc = item.split(',"gu":"')[1].split('"')[0].replace("\\", "")
                    lat = item.split(',"lat":"')[1].split('"')[0]
                    lng = item.split('"lng":"')[1].split('"')[0]
                    add = item.split('"st":"')[1].split('"')[0]
                    zc = item.split('"zp":"')[1].split('"')[0]
                    city = item.split('"ct":"')[1].split('"')[0]
                    state = item.split('"rg":"')[1].split('"')[0]
                    phone = item.split('"te":"')[1].split('"')[0]
                    store = item.split('"')[0]
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
