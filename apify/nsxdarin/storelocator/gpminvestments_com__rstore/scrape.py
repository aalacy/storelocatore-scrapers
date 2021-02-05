import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import usaddress

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("gpminvestments_com__rstore")


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
                "raw_address",
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
    url = "https://gpminvestments.com/store-locator/"
    r = session.get(url, headers=headers)
    website = "gpminvestments.com/rstore"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    hours = "<MISSING>"
    phone = "<MISSING>"
    add = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zc = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"marker_id":"' in line:
            items = line.split('"marker_id":"')
            for item in items:
                if '"title":"' in item:
                    store = item.split('"')[0]
                    rawadd = (
                        item.split(',"address":"')[1]
                        .split('"')[0]
                        .replace("  ", " ")
                        .replace("  ", " ")
                    )
                    name = item.split('"title":"')[1].split('"')[0]
                    lat = item.split('"lat":"')[1].split('"')[0]
                    lng = item.split('"lng":"')[1].split('"')[0]
                    try:
                        add = usaddress.tag(rawadd)
                        address = (
                            add[0]["AddressNumber"]
                            + " "
                            + add[0]["StreetName"]
                            + " "
                            + add[0]["StreetNamePostType"]
                        )
                        if add == "":
                            add = "<INACCESSIBLE>"
                        city = add[0]["PlaceName"]
                        state = add[0]["StateName"]
                        zc = add[0]["ZipCode"]
                    except:
                        pass
                    yield [
                        website,
                        loc,
                        name,
                        rawadd,
                        address,
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
