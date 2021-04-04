import csv
import json
import time

from datetime import date

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

    base_link = "https://www.stantonoptical.com/schedule-exam/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    locator_domain = "stantonoptical.com"

    script = (
        base.find("script", attrs={"type": "application/json"})
        .text.replace("\n", "")
        .strip()
    )
    stores = json.loads(script)["props"]["stores"]

    for store in stores:
        location_name = store["WebDescription"].strip()
        street_address = (
            store["AddressLine1"]
            + " "
            + store["AddressLine2"]
            + " "
            + store["AddressLine3"]
        ).strip()
        city = store["City"]
        state = store["State"]
        zip_code = store["PostalCode"]
        country_code = store["Country"]
        store_number = store["StoreNumber"]

        try:
            latitude = store["Latitude"]
            longitude = store["Longitude"]
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        if not latitude:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        location_type = store["PosDescription"].split("-")[0]

        try:
            if "eye" in location_type.lower():
                link = "https://www.myeyelab.com/locations/" + store["webPath"]
            else:
                link = "https://www.stantonoptical.com/locations/" + store["webPath"]
        except:
            continue

        phone = "<MISSING>"

        try:
            mon = (
                "Monday "
                + store["MondayStart"].split(".")[0]
                + "-"
                + store["MondayEnd"].split(".")[0]
            )
        except:
            mon = "Monday Closed"

        try:
            tue = (
                " Tuesday "
                + store["TuesdayStart"].split(".")[0]
                + "-"
                + store["TuesdayEnd"].split(".")[0]
            )
        except:
            tue = " Tuesday Closed"

        try:
            wed = (
                " Wednesday "
                + store["WednesdayStart"].split(".")[0]
                + "-"
                + store["WednesdayEnd"].split(".")[0]
            )
        except:
            wed = " Wednesday Closed"

        try:
            thu = (
                " Thursday "
                + store["ThursdayStart"].split(".")[0]
                + "-"
                + store["ThursdayEnd"].split(".")[0]
            )
        except:
            thu = " Thursday Closed"

        try:
            fri = (
                " Friday "
                + store["FridayStart"].split(".")[0]
                + "-"
                + store["FridayEnd"].split(".")[0]
            )
        except:
            fri = " Friday Closed"

        try:
            sat = (
                " Saturday "
                + store["SaturdayStart"].split(".")[0]
                + "-"
                + store["SaturdayEnd"].split(".")[0]
            )
        except:
            sat = " Saturday Closed"

        try:
            sun = (
                " Sunday "
                + store["SundayStart"].split(".")[0]
                + "-"
                + store["SundayEnd"].split(".")[0]
            )
        except:
            sun = " Sunday Closed"

        hours_of_operation = mon + tue + wed + thu + fri + sat + sun

        open_date = store["StoreOpeningDate"].split("T")[0]
        today = date.today().strftime("%Y-%m-%d")

        open_date = time.strptime(open_date, "%Y-%m-%d")
        today = time.strptime(today, "%Y-%m-%d")

        if open_date > today:
            hours_of_operation = "Coming Soon"

        phone = "<INACCESSIBLE>"

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
