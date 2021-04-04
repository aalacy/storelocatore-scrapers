import csv
from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


URL = "https://api.pressedjuicery.com/stores?sort=name"
DOMAIN = "pressedjuicery.com"

session = SgRequests()

HEADERS = {
    "Host": "api.pressedjuicery.com",
    "Origin": "https://api.pressedjuicery.com/stores?sort=name",
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
}


def parse_hours(store):
    ret = []
    days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    for i in range(7):
        start_time = store[days[i]]["start"]
        end_time = store[days[i]]["end"]
        if start_time is not None and end_time is not None:
            if int(str(start_time)[:2]) > 12:
                start = (
                    "0"
                    + str(store[days[i]]["start"])[:1]
                    + ":"
                    + str(store[days[i]]["start"])[1:]
                )
            else:
                start = (
                    str(store[days[i]]["start"])[:2]
                    + ":"
                    + str(store[days[i]]["start"])[2:]
                )
            close = (
                str(store[days[i]]["end"])[:2] + ":" + str(store[days[i]]["end"])[2:]
            )
            day = days[i]
            ret.append("{}: {}-{}".format(day, start, close))
        else:
            day = days[i]
            ret.append("{}: CLOSED".format(day))

    return ", ".join(ret)


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def fetch_data():
    stores = session.get(URL, headers=HEADERS).json()["stores"]
    locations = []
    for store in stores:
        locator_domain = DOMAIN
        page_url = "https://pressedjuicery.com/pages/juice-bar-locations"
        location_name = handle_missing(store["name"])
        street_address = handle_missing(store["streetAddress"])
        city = handle_missing(store["locality"])
        state = handle_missing(store["region"])
        zip_code = handle_missing(store["postal"])
        country_code = handle_missing(store["country"])
        store_number = store["id"]
        phone = handle_missing(store["phone"])
        location_type = "<MISSING>"
        latitude = handle_missing(store["geometry"]["coordinates"][1])
        if latitude == 0.0:
            latitude = "<MISSING>"
        longitude = handle_missing(store["geometry"]["coordinates"][0])
        if longitude == 0.0:
            longitude = "<MISSING>"
        hours_of_operation = handle_missing(parse_hours(store["storeHours"]))
        locations.append(
            [
                locator_domain,
                page_url,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
        )
    return locations


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
