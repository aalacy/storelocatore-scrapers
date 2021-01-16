import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("ta-petro_com")


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
    url = "https://www.ta-petro.com/api/locations/get"
    r = session.post(url, headers=headers)
    website = "ta-petro.com"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"BrandId":' in line:
            items = line.split('"BrandId":')
            for item in items:
                if '"TASiteNumber":"' in item:
                    hours = "<MISSING>"
                    store = item.split('"TASiteNumber":"')[1].split('"')[0]
                    name = item.split('"Name":"')[1].split('"')[0] + " #" + store
                    add = item.split('"Street":"')[1].split('"')[0]
                    city = item.split('"City":"')[1].split('"')[0]
                    state = item.split('"State":"')[1].split('"')[0]
                    zc = item.split('"PostalCode":"')[1].split('"')[0]
                    phone = item.split('"Phone":"')[1].split('"')[0]
                    lat = item.split('"Latitude":')[1].split(",")[0]
                    lng = item.split('"Longitude":')[1].split(",")[0]
                    loc = (
                        "https://www.ta-petro.com/location/"
                        + state
                        + "/"
                        + item.split(',"FileName":"')[1].split('"')[0]
                    )
                    try:
                        logger.info(loc)
                        r2 = session.get(loc, headers=headers)
                        lines = r2.iter_lines()
                        for line2 in lines:
                            line2 = str(line2.decode("utf-8"))
                            if "In-Bay Service Hours:</strong>" in line2:
                                g = next(lines)
                                g = next(lines)
                                g = str(g.decode("utf-8"))
                                hours = g.split(">")[1].split("<")[0]
                    except:
                        hours = "<INACCESSIBLE>"
                    if "Petro" in name:
                        typ = "Petro"
                    elif "TA Express" in name:
                        typ = "TA Express"
                    else:
                        typ = "TA"
                    if hours == "":
                        hours = "24/7/365"
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
