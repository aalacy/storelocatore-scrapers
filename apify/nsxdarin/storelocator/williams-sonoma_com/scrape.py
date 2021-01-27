import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("williams-sonoma_com")


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
    url = "https://www.williams-sonoma.com/search/stores.json?brands=WS&lat=47.6186&lng=-122.204&radius=10000&includeOutlets=false"
    r = session.get(url, headers=headers)
    website = "williams-sonoma.com"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '{"properties":' in line:
            items = line.split('{"properties":')
            for item in items:
                if '"DISTANCE":"' in item:
                    typ = "<MISSING>"
                    store = item.split('"STORE_NUMBER":"')[1].split('"')[0]
                    add = (
                        item.split('"ADDRESS_LINE_1":"')[1].split('"')[0]
                        + " "
                        + item.split('"ADDRESS_LINE_2":"')[1].split('"')[0]
                    )
                    phone = item.split('"PHONE_NUMBER_FORMATTED":"')[1].split('"')[0]
                    name = item.split('"STORE_NAME":"')[1].split('"')[0]
                    city = item.split('"CITY":"')[1].split('"')[0]
                    state = item.split('"STATE_PROVINCE":"')[1].split('"')[0]
                    zc = item.split(',"POSTAL_CODE":"')[1].split('"')[0]
                    lat = item.split('"LATITUDE":"')[1].split('"')[0]
                    lng = item.split('"LONGITUDE":"')[1].split('"')[0]
                    country = item.split('"COUNTRY_CODE":"')[1].split('"')[0]
                    loc = "<MISSING>"
                    hours = (
                        "Sun: "
                        + item.split('"SUNDAY_HOURS_FORMATTED":"')[1].split('"')[0]
                    )
                    hours = (
                        hours
                        + "; Mon: "
                        + item.split('"MONDAY_HOURS_FORMATTED":"')[1].split('"')[0]
                    )
                    hours = (
                        hours
                        + "; Tue: "
                        + item.split('"TUESDAY_HOURS_FORMATTED":"')[1].split('"')[0]
                    )
                    hours = (
                        hours
                        + "; Wed: "
                        + item.split('"WEDNESDAY_HOURS_FORMATTED":"')[1].split('"')[0]
                    )
                    hours = (
                        hours
                        + "; Thu: "
                        + item.split('"THURSDAY_HOURS_FORMATTED":"')[1].split('"')[0]
                    )
                    hours = (
                        hours
                        + "; Fri: "
                        + item.split('"FRIDAY_HOURS_FORMATTED":"')[1].split('"')[0]
                    )
                    hours = (
                        hours
                        + "; Sat: "
                        + item.split('"SATURDAY_HOURS_FORMATTED":"')[1].split('"')[0]
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
