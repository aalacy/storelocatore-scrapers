import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("portofsubs_com")


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
    url = "https://order.portofsubs.com/locations?clear_default=true"
    r = session.get(url, headers=headers)
    website = "portofsubs.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'console.log("Port of Subs #' in line:
            name = line.split('console.log("')[1].split('"')[0]
            store = name.split("#")[1]
        if 'address: "' in line:
            addinfo = line.split('address: "')[1].split('"')[0]
            add = addinfo.split("<")[0].strip()
            city = addinfo.split("<br>")[1].split(",")[0]
            state = addinfo.split("<br>")[1].split(",")[1].strip().split(" ")[0]
            zc = addinfo.rsplit(" ", 1)[1]
        if "href='tel:" in line:
            phone = line.split("href='tel:")[1].split("'")[0]
        if 'geo:  "' in line:
            lat = line.split('geo:  "')[1].split(",")[0]
            lng = line.split(",")[1].split('"')[0]
            hours = "<MISSING>"
        if "supportsonlineordering" in line:
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
