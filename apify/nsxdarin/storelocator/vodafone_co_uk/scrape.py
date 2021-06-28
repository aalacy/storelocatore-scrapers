import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("vodafone_co_uk")


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
    url = "https://www.vodafone.co.uk/help-and-information/store-locator"
    r = session.get(url, headers=headers)
    website = "vodafone.co.uk"
    typ = "<MISSING>"
    country = "GB"
    loc = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"CMSStoreLocator":{"jsonData"' in line:
            items = line.split("storecode")
            for item in items:
                if "eshoptown" in item:
                    store = item.split('\\": \\"')[1].split("\\")[0]
                    name = item.split('"name\\": \\"')[1].split('\\",')[0].strip()
                    city = item.split('eshoptown\\": \\"')[1].split('\\"')[0].strip()
                    state = "<MISSING>"
                    zc = item.split('"postcode\\": \\"')[1].split("\\")[0].strip()
                    lat = item.split('"lat\\": \\"')[1].split("\\")[0].strip()
                    lng = item.split('"lng\\": \\"')[1].split("\\")[0].strip()
                    hours = item.split('"hours\\": \\"')[1].split('\\"')[0].strip()
                    if "Store Mobile:" in hours:
                        phone = hours.split("Store Mobile:")[1].strip()
                    if ", Store" in hours:
                        hours = hours.split(", Store")[0].strip()
                    add = item.split('"address\\": \\"')[1].split('\\",')[0]
                    add = (
                        add.replace("  ", " ")
                        .replace("  ", " ")
                        .replace("  ", " ")
                        .replace(" ,", ",")
                    )
                    ctext = ", " + city
                    if ctext in add:
                        add = add.rsplit(ctext, 1)[0].strip()
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
