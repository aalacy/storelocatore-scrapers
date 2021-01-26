import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("oxxousa_com")


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
    url = "https://oxxousa.us/wp-admin/admin-ajax.php?action=store_search&lat=26.012254&lng=-80.144378&max_results=100&search_radius=5000&autoload=1"
    r = session.get(url, headers=headers)
    website = "oxxousa.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '{"address":"' in line:
            items = line.split('{"address":"')
            for item in items:
                if '"description":"' in item:
                    loc = item.split('"permalink":"')[1].split('"')[0].replace("\\", "")
                    if loc == "":
                        loc = "<MISSING>"
                    add = item.split('"')[0]
                    store = item.split('"id":"')[1].split('"')[0]
                    add = add + " " + item.split('"address2":"')[1].split('"')[0]
                    add = add.strip()
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0]
                    zc = item.split('"zip":"')[1].split('"')[0]
                    lat = item.split('"lat":"')[1].split('"')[0]
                    lng = item.split('"lng":"')[1].split('"')[0]
                    phone = item.split('"phone":"')[1].split('"')[0]
                    if phone == "":
                        phone = "<MISSING>"
                    name = item.split('"store":"')[1].split('","thumb')[0]
                    if '\\">' in name:
                        name = name.split('\\">')[1]
                    name = name.replace("&#8211;", "-")
                    if "<" in name:
                        name = name.split("<")[0].strip()
                    hours = item.split('"wpsl-opening-hours\\"><tr><td>')[1].split(
                        '<\\/table>"'
                    )[0]
                    hours = hours.replace("<\\/td><td><time>", ": ").replace(
                        "<\\/time><\\/td><\\/tr><tr><td>", "; "
                    )
                    hours = hours.replace("<\\/td><td>Closed<\\/td><\\/tr>", ": Closed")
                    if "oxxo-care-cleaners-aventura" in loc:
                        name = "OXXO Care Cleaners - Aventura"
                    if city == "Doral":
                        state = "FL"
                    if zc == "" and city == "North Miami":
                        zc = "33181"
                    if zc == "":
                        zc = "<MISSING>"
                    name = name.replace("\\u2013", "-")
                    name = name.replace("\\u00a0", "")
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
