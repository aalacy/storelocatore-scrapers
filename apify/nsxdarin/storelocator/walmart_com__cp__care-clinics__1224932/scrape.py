import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("walmart_com__cp__care-clinics__1224932")


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
    url = "https://www.walmart.com/cp/care-clinics/1224932"
    r = session.get(url, headers=headers)
    website = "walmart.com/cp/care-clinics/1224932"
    typ = "Care Clinic"
    country = "US"
    loc = "<MISSING>"
    store = "<MISSING>"
    hours = ""
    lat = "<MISSING>"
    lng = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = (
            str(line.decode("utf-8"))
            .replace("%20", " ")
            .replace("%3E", ">")
            .replace("%2F", "/")
            .replace("%2C", ",")
            .replace("%3C", "<")
            .replace("%3D", "=")
        )
        if "'address" in line:
            items = line.split("'address")
            for item in items:
                if "hours" in item and 'egory" type="application/json"' not in item:
                    name = "Walmart Care Clinic"
                    addinfo = item.split(">")[1].split("<")[0]
                    addinfo = addinfo.replace("AR, ", "AR ")
                    zc = addinfo.rsplit(" ", 1)[1]
                    state = addinfo.rsplit(",", 1)[1].strip().split(" ")[0]
                    add = addinfo.split(",")[0]
                    city = addinfo.rsplit(",", 1)[0].strip().rsplit(" ", 1)[1]
                    phone = (
                        item.split(">Ph")[1]
                        .split("<")[0]
                        .replace(".", "")
                        .replace("%3A", "")
                    )
                    hours = (
                        item.split("class='td hours' aria-label='")[1]
                        .split(">")[0]
                        .replace("%3A", ":")
                    )
                    add = add.replace(city, "").strip()
                    hours = hours.replace("'", "")
                    if "4870 Elm" in add:
                        add = add + " Suite B"
                    if "4221 Atlanta" in add:
                        add = add + " Suite 101"
                        city = "Loganville"
                        state = "GA"
                        zc = "30052"
                    if "494 W" in add:
                        city = "Royse City"
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
