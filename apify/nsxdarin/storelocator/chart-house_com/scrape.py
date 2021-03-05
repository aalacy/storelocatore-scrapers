import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("chart-house_com")


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
    url = "https://www.chart-house.com/store-locator/"
    r = session.get(url, headers=headers)
    website = "chart-house.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "locations:" in line:
            line = line.replace('"categories": [{"name"', "")
            items = line.split('{"name": "')
            for item in items:
                if '"slug": "' in item:
                    loc = (
                        "https://www.chart-house.com"
                        + item.split('"url": "')[1].split('"')[0]
                    )
                    name = item.split('"')[0]
                    add = item.split('"street": "')[1].split('"')[0]
                    city = item.split('"city": "')[1].split('"')[0]
                    state = item.split('"state": "')[1].split('"')[0]
                    zc = item.split('"postal_code": "')[1].split('"')[0]
                    lat = item.split('"lat": "')[1].split('"')[0]
                    lng = item.split('"lng": "')[1].split('"')[0]
                    phone = item.split('"phone_number": "')[1].split('"')[0]
                    store = "<MISSING>"
                    hours = item.split('"hours": "\\u003cp\\u003e')[1].split(
                        '", "structured_hours":'
                    )[0]
                    if "\\u003cbr/\\u003e\\u003ch4\\u003ePick Up:" in hours:
                        hours = hours.split(
                            "\\u003cbr/\\u003e\\u003ch4\\u003ePick Up:"
                        )[0]
                    if "\\u003cbr/\\u003eHappy Hour:" in hours:
                        hours = hours.split("\\u003cbr/\\u003eHappy Hour:")[0]
                    hours = hours.replace("\\u003cbr/\\u003e", "; ")
                    if "; Closing times" in hours:
                        hours = hours.split("; Closing times")[0]
                    if "; Happy Hour" in hours:
                        hours = hours.split("; Happy Hour")[0]
                    if "; Open for To Go" in hours:
                        hours = hours.split("; Open for To Go")[0]
                    if "chart-house-san-antonio-tx" in loc:
                        hours = "Monday - Thursday: 4:00 pm - 10:00 pm; Friday - Saturday: 12:00 pm - 11:00 pm; Sunday: 12:00 pm - 10:00 pm"
                    name = name.replace("\\u0027", "'")
                    add = add.replace("\\u0027", "'")
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
