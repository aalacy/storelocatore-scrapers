import csv
from sgrequests import SgRequests
import json


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


def fetch_data():
    # Your scraper here
    locator_domain = "https://www.brookshires.com/"
    csrfURL = "https://www.brookshires.com/api/m_user/sessioninit"
    locationsURL = (
        "https://www.brookshires.com/api/m_store_location?store_type_ids=1,2,3"
    )
    missingString = "<MISSING>"

    s = SgRequests()

    csrf = json.loads(s.post(csrfURL).text)[0]

    headers = {"x-csrf-token": csrf}

    locations = json.loads(s.get(locationsURL, headers=headers).text)["stores"]

    result = []

    for s in locations:
        store_name = s["storeName"]
        store_number = s["store_number"]
        store_zip = s["zip"]
        store_phone = s["phone"]
        lat = s["latitude"]
        lng = s["longitude"]
        country = s["country"]
        address = s["address"]
        city = s["city"]
        hours_array = []
        for d in s["store_hours"]:
            day = ""
            if d["day"] == 0:
                day = "Monday"
            if d["day"] == 1:
                day = "Tuesday"
            if d["day"] == 2:
                day = "Wednesday"
            if d["day"] == 3:
                day = "Thursday"
            if d["day"] == 4:
                day = "Friday"
            if d["day"] == 5:
                day = "Saturday"
            if d["day"] == 6:
                day = "Sunday"
            hours_array.append("{} : {} - {}".format(day, d["open"], d["close"]))
        store_hours = ", ".join(str(x) for x in hours_array)

        result.append(
            [
                locator_domain,
                missingString,
                store_name,
                address,
                city,
                country,
                store_zip,
                missingString,
                store_number,
                store_phone,
                missingString,
                lat,
                lng,
                store_hours,
            ]
        )

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
