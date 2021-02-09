import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json
import datetime

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/json",
}

logger = SgLogSetup().get_logger("milliescookies_com")


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
    url = "https://www.milliescookies.com/m2api/locateStore"
    payload = {
        "address": "london",
        "country": "uk",
        "limit": "100",
        "maxDistance": "5000",
    }
    r = session.post(url, headers=headers, data=json.dumps(payload))
    website = "milliescookies.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    logger.info("Pulling Stores")
    for item in json.loads(r.content)["stores"]:
        hours = ""
        add = item["address"]
        country = item["country_id"]
        store = item["id"]
        city = item["city"]
        name = item["store_name"]
        lat = item["latitude"]
        lng = item["longitude"]
        phone = item["phone"]
        try:
            state = item["state"]
        except:
            state = "<MISSING>"
        zc = item["postcode"]
        days = str(item).split("'20")
        dc = 0
        for day in days:
            if "'open': '" in day:
                dc = dc + 1
                dayname = day.split("'")[0]
                dayname = "20" + dayname
                year, month, dayt = (int(x) for x in dayname.split("-"))
                wd = datetime.date(year, month, dayt).weekday()
                if wd == 1:
                    day_name = "Mon"
                if wd == 2:
                    day_name = "Tue"
                if wd == 3:
                    day_name = "Wed"
                if wd == 4:
                    day_name = "Thu"
                if wd == 5:
                    day_name = "Fri"
                if wd == 6:
                    day_name = "Sat"
                if wd == 0:
                    day_name = "Sun"
                hrs = (
                    day_name
                    + ": "
                    + day.split("{'open': '")[1].split("'")[0]
                    + "-"
                    + day.split("'close': '")[1].split("'")[0]
                )
                if dc <= 7:
                    if hours == "":
                        hours = hrs
                    else:
                        hours = hours + "; " + hrs
        add = add.replace(", Bluewater", "").replace(" LE1 4FR, United Kingdom", "")
        add = (
            add.replace(", Birmingham", "")
            .replace(", Dudley", "")
            .replace(", Nottingham", "")
            .replace(", Cardiff", "")
        )
        add = (
            add.replace(", Sheffield", "")
            .replace(", Manchester", "")
            .replace(", Murton", "")
            .replace(", Gateshead", "")
            .replace(", Newcastle", "")
            .replace(", Glasgow", "")
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
