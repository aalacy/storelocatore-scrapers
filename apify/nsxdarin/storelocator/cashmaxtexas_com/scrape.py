import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("cashmaxtexas_com")


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
    url = "https://www.cashmaxtexas.com/locations.html"
    r = session.get(url, headers=headers)
    website = "cashmaxtexas.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '{"@type":"LocalBusiness","name":"CashMax Title & Loan"' in line:
            items = line.split('{"@type":"LocalBusiness","name":"CashMax Title & Loan"')
            for item in items:
                if (
                    '"@id":"https://www.cashmaxtexas.com/' in item
                    and "#organization" not in item
                ):
                    loc = item.split('"url":"')[1].split('"')[0]
                    hours = ""
                    phone = item.split('"telephone":"+1-')[1].split('"')[0]
                    add = item.split('streetAddress":"')[1].split('"')[0]
                    zc = item.split('postalCode":"')[1].split('"')[0]
                    state = item.split('addressRegion":"')[1].split('"')[0]
                    city = item.split('addressLocality":"')[1].split('"')[0]
                    name = "Cash Max " + city
                    lat = "<MISSING>"
                    lng = "<MISSING>"
                    store = "<MISSING>"
                    days = item.split('"dayOfWeek":["')
                    for day in days:
                        if ',"opens":"' in day:
                            hrs = (
                                day.split('"]')[0].replace('","', "-")
                                + ": "
                                + day.split(',"opens":"')[1].split('"')[0]
                                + "-"
                                + day.split('"closes":"')[1].split('"')[0]
                            )
                            hrs = hrs.replace("00:00-00:00", "Closed")
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
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
