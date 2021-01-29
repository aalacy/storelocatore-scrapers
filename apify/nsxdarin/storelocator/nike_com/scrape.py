import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("nike_com")


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
    url = "https://nike.brickworksoftware.com/api/v3/stores.json"
    r = session.get(url, headers=headers, timeout=90)
    website = "nike.com"
    typ = "<MISSING>"
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"slug":"' in line:
            items = line.split('"slug":"')
            for item in items:
                if '"name":"' in item:
                    name = item.split('"name":"')[1].split('"')[0]
                    loc = "https://www.nike.com/us/retail/s/" + item.split('"')[0]
                    add = item.split('"address_1":"')[1].split('"')[0]
                    try:
                        add = add + " " + item.split('"address_2":"')[1].split('"')[0]
                    except:
                        pass
                    city = item.split('"city":"')[1].split('"')[0]
                    try:
                        state = item.split('"state":"')[1].split('"')[0]
                    except:
                        state = "<MISSING>"
                    try:
                        country = item.split('"country_code":"')[1].split('"')[0]
                    except:
                        country = "<MISSING>"
                    try:
                        zc = item.split('"postal_code":"')[1].split('"')[0]
                    except:
                        zc = "<MISSING>"
                    try:
                        store = item.split('"number":"')[1].split('"')[0]
                    except:
                        store = "<MISSING>"
                    try:
                        phone = item.split('"phone_number":"')[1].split('"')[0]
                    except:
                        phone = "<MISSING>"
                    try:
                        lat = item.split('"latitude":')[1].split(",")[0]
                        lng = item.split('"longitude":')[1].split(",")[0]
                    except:
                        lat = "<MISSING>"
                        lng = "<MISSING>"
                    try:
                        days = (
                            item.split('"regular_hours":[{')[1]
                            .split("]")[0]
                            .split('"start_time":"')
                        )
                        hours = ""
                        for day in days:
                            if '"end_time":"' in day:
                                if '"closed":true' in day:
                                    hrs = (
                                        day.split('"display_day":"')[1].split('"')[0]
                                        + ": Closed"
                                    )
                                else:
                                    hrs = (
                                        day.split('"display_day":"')[1].split('"')[0]
                                        + ": "
                                        + day.split('"display_start_time":"')[1].split(
                                            '"'
                                        )[0]
                                        + "-"
                                        + day.split('"display_end_time":"')[1].split(
                                            '"'
                                        )[0]
                                    )
                                if hours == "":
                                    hours = hrs
                                else:
                                    hours = hours + "; " + hrs
                    except:
                        hours = "<MISSING>"
                    if country == "CA" or country == "US" or country == "GB":
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
