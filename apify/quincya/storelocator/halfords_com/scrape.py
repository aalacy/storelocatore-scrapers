import csv
import json

from bs4 import BeautifulSoup

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


def fetch_data():

    base_link = "https://www.halfords.com/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    stores = json.loads(base.find(class_="js-stores").text)["stores"]

    data = []
    locator_domain = "halfords.com"

    for store in stores:
        location_name = store["name"]
        try:
            street_address = (store["address1"] + " " + store["address2"]).strip()
        except:
            try:
                street_address = store["address1"].strip()
            except:
                continue
        city = store["city"]
        try:
            state = store["stateCode"]
        except:
            state = "<MISSING>"
        zip_code = store["postalCode"]
        country_code = "UK"
        phone = store["phone"]
        latitude = store["latitude"]
        longitude = store["longitude"]
        store_number = store["ID"]
        link = store["storeDetailsLink"]
        location_type = store["storeType"]
        if not location_type:
            if "auto" in link:
                location_type = "Halfords Autocentre"
            else:
                location_type = "Halfords"

        hours_of_operation = ""
        raw_hours = store["storeHours"]["workingHours"][0]
        for hour in raw_hours:
            try:
                time_str = (
                    raw_hours[hour][0]["Start"] + "-" + raw_hours[hour][0]["Finish"]
                )
            except:
                time_str = "Closed"
            hours_of_operation = (
                hours_of_operation + " " + hour + ": " + time_str
            ).strip()
        try:
            msg = str(store["custom"]["emergencyMessage"])
            if "now closed" in msg:
                continue
            if "currently closed" in msg:
                hours_of_operation = "Currently Closed"
            if "temporarily closed" in msg:
                hours_of_operation = "Temporarily Closed"
        except:
            pass

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
