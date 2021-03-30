import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("unitedsupermarkets_com")


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
    url = "https://www.unitedsupermarkets.com/RS.Relationshop/StoreLocation/GetListClosestStores"
    r = session.get(url, headers=headers)
    website = "unitedsupermarkets.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '{"Distance":' in line:
            items = line.split('{"Distance":')
            for item in items:
                if '"Logo":"' in item:
                    name = item.split('"StoreName":"')[1].split('"')[0]
                    city = item.split('"City":"')[1].split('"')[0]
                    add = item.split('"Address1":"')[1].split('"')[0]
                    store = item.split('"StoreID":')[1].split(",")[0]
                    loc = (
                        "https://www.unitedsupermarkets.com/rs/StoreLocator?id=" + store
                    )
                    state = item.split('"State":"')[1].split('"')[0]
                    zc = item.split('"Zipcode":"')[1].split('"')[0]
                    phone = item.split('"PhoneNumber":"')[1].split('"')[0]
                    lat = item.split('"Latitude":')[1].split(",")[0]
                    lng = item.split('"Longitude":')[1].split(",")[0]
                    hours = item.split('"StoreHours":"')[1].split('"')[0]
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
