import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "authorization": "Bearer 90dd1fcea0074e7eb4b11e3753a0a334",
}

logger = SgLogSetup().get_logger("prohealthcare_com")


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
    urls = [
        "https://d2ez0zkh6r5hup.cloudfront.net/v2/locations?group_ids=bQ2rmQ&origin=react_mobile_app&filters=locations.is_test_location:false;&page=2",
        "https://d2ez0zkh6r5hup.cloudfront.net/v2/locations?group_ids=bQ2rmQ&origin=react_mobile_app&filters=locations.is_test_location:false;",
    ]
    for url in urls:
        r = session.get(url, headers=headers)
        website = "prohealthcare.com"
        typ = "<MISSING>"
        country = "US"
        loc = "<MISSING>"
        store = "<MISSING>"
        hours = "<MISSING>"
        logger.info("Pulling Stores")
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '"accepted_insurances":' in line:
                items = line.split('"accepted_insurances":')
                for item in items:
                    if "accepted_insurers" in item:
                        name = item.split('"name": "')[1].split('"')[0]
                        add = item.split('"address": "')[1].split('"')[0]
                        city = item.split('"city": "')[1].split('"')[0]
                        state = item.split('"state": "')[1].split('"')[0]
                        zc = item.split('"zip_code": "')[1].split('"')[0]
                        lat = item.split('"lat_long": "(')[1].split(",")[0]
                        lng = (
                            item.split('"lat_long": "(')[1].split(",")[1].split(")")[0]
                        )
                        phone = (
                            item.split('"phone": "')[1].split('"')[0].replace("+1", "")
                        )
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
