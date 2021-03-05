import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("thebookrack_com")


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
    url = "https://thebookrack.com/locations/"
    r = session.get(url, headers=headers)
    website = "thebookrack.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<td class="column-1">' in line:
            name = "The Book Rack"
            add = line.split('<td class="column-1">')[1].split("<")[0]
            city = line.split('<td class="column-2">')[1].split("<")[0]
            state = line.split('<td class="column-3">')[1].split("<")[0]
            phone = line.split('<td class="column-4">')[1].split("<")[0]
            if phone == "":
                phone = "<MISSING>"
            store = "<MISSING>"
            zc = "<MISSING>"
            lat = "<MISSING>"
            lng = "<MISSING>"
            hours = "<MISSING>"
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
