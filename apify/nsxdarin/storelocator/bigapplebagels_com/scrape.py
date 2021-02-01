import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("bigapplebagels_com")


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
    url = "https://bigapplebagels.com/Umbraco/Api/LocationsApi/GetNearbyLocations?latitude=40.75&longitude=-73.99&maxResults=&maxDistance=5000"
    r = session.get(url, headers=headers)
    website = "bigapplebagels.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    store = "<MISSING>"
    hours = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"Longitude":' in line:
            items = line.split('"Longitude":')
            for item in items:
                if '"Latitude":' in item:
                    add = ""
                    lng = item.split(",")[0]
                    lat = item.split('"Latitude":')[1].split(",")[0]
                    name = item.split('"Name":"')[1].split('"')[0]
                    try:
                        add = item.split('"Address2":"')[1].split('"')[0]
                    except:
                        add = ""
                    if add == "":
                        try:
                            add = item.split('"Address1":"')[1].split('"')[0]
                        except:
                            pass
                    else:
                        try:
                            add = (
                                add + " " + item.split('"Address1":"')[1].split('"')[0]
                            )
                        except:
                            pass
                    city = item.split('"Locality":"')[1].split('"')[0]
                    state = item.split('"Region":"')[1].split('"')[0]
                    zc = item.split('"PostalCode":"')[1].split('"')[0]
                    phone = item.split('"Phone":"')[1].split('"')[0]
                    store = item.split('"ID":')[1].split(",")[0]
                    hours = "<MISSING>"
                    if phone == "":
                        phone = "<MISSING>"
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
