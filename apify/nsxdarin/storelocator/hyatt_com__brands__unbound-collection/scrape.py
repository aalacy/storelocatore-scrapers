import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("hyatt_com__brands__unbound-collection")


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
    url = "https://www.hyatt.com/explore-hotels/map/filter?brands=The%20Unbound%20Collection%20by%20Hyatt"
    r = session.get(url, headers=headers)
    website = "hyatt.com/brands/unbound-collection"
    typ = "<MISSING>"
    hours = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '{"info":' in line:
            items = line.split('{"info":')
            for item in items:
                if '"name":"' in item:
                    store = item.split('"spiritCode":"')[1].split('"')[0]
                    name = item.split('"name":"')[1].split('"')[0]
                    loc = item.split('"propertySiteUrl":"')[1].split('"')[0]
                    add = item.split('"address":{"address1":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    try:
                        state = item.split('"state":"')[1].split('"')[0]
                    except:
                        state = "<MISSING>"
                    zc = "<MISSING>"
                    country = item.split('"country":"')[1].split('"')[0]
                    lat = item.split('"latitude":')[1].split(",")[0]
                    lng = item.split('"longitude":')[1].split("}")[0]
                    phone = "<MISSING>"
                    r2 = session.get(loc, headers=headers)
                    for line2 in r2.iter_lines():
                        line2 = str(line2.decode("utf-8"))
                        if 'Tel: <a href="tel:' in line2:
                            phone = (
                                line2.split('Tel: <a href="tel:')[1]
                                .split('">')[1]
                                .split("<")[0]
                            )
                    if (
                        country == "United States"
                        or country == "Canada"
                        or country == "United Kingdom"
                    ):
                        if "States" in country:
                            country = "US"
                        if country == "Canada":
                            country = "CA"
                        if country == "United Kingdom":
                            country = "GB"
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
