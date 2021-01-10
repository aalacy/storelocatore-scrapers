import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("koiautoparts_com")


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
    url = "https://www.koiautoparts.com/map/data/locations.xml"
    r = session.get(url, headers=headers)
    website = "koiautoparts.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    store = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<marker name="' in line:
            name = line.split('<marker name="')[1].split('"')[0]
            lat = line.split('lat="')[1].split('"')[0]
            lng = line.split('lng="')[1].split('"')[0]
            add = line.split('address="')[1].split('"')[0]
            city = line.split('city="')[1].split('"')[0]
            state = line.split('state="')[1].split('"')[0]
            zc = line.split('postal="')[1].split('"')[0]
            phone = line.split('phone="')[1].split('"')[0]
            hours = line.split('hours1="')[1].split('"')[0]
            hours = hours + "; " + line.split('hours2="')[1].split('"')[0]
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
