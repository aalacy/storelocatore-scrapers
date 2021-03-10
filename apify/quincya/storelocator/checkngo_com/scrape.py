import csv
import json

from bs4 import BeautifulSoup

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    data = []
    locator_domain = "checkngo.com"

    base_link = "https://locations.checkngo.com/service/location/getlocationsnear?latitude=35.5094529&longitude=-97.64396110000001&radius=10000&brandFilter=Check%20`n%20Go"
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    stores = json.loads(base.text.strip())

    for store in stores:
        location_name = store["ColloquialName"]
        street_address = (store["Address1"] + " " + store["Address2"]).strip()
        city = store["City"]
        state = store["State"]["Code"]
        zip_code = store["ZipCode"]
        country_code = "US"
        store_number = store["StoreNum"]
        location_type = "<MISSING>"
        phone = store["FormattedPhone"]

        if not store["MondayOpen"]:
            mon = "Closed"
        else:
            mon = store["MondayOpen"] + "-" + store["MondayClose"]

        if not store["TuesdayOpen"]:
            tue = "Closed"
        else:
            tue = store["TuesdayOpen"] + "-" + store["TuesdayClose"]

        if not store["WednesdayOpen"]:
            wed = "Closed"
        else:
            wed = store["WednesdayOpen"] + "-" + store["WednesdayClose"]

        if not store["ThursdayOpen"]:
            thu = "Closed"
        else:
            thu = store["ThursdayOpen"] + "-" + store["ThursdayClose"]

        if not store["FridayOpen"]:
            fri = "Closed"
        else:
            fri = store["FridayOpen"] + "-" + store["FridayClose"]

        hours_of_operation = (
            "Monday "
            + mon
            + " Tuesday "
            + tue
            + " Wednesday "
            + wed
            + " Thursday "
            + thu
            + " Friday "
            + fri
        ).strip()

        try:
            sat = " Saturday " + store["SaturdayOpen"] + "-" + store["SaturdayClose"]
        except:
            sat = " Saturday INACCESSIBLE"
        try:
            sun = " Sunday " + store["SundayOpen"] + "-" + store["SundayClose"]
        except:
            sun = " Sunday INACCESSIBLE"

        hours_of_operation = hours_of_operation + sat + sun

        latitude = store["Latitude"]
        if latitude == 33.2:
            latitude = "33.2000"
        longitude = store["Longitude"]
        link = "https://locations.checkngo.com/locations" + store["Url"]

        # Store data
        data.append(
            [
                locator_domain,
                link,
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
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
