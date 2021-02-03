import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("astonmartin_com")
session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    r = session.get(
        "https://www.astonmartin.com/api/v1/dealers?latitude=46.8628313&longitude=-96.8188352&cultureName=en-US&take=200"
    ).json()
    location_name = "<MISSING>"
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "<MISSING>"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"
    for loc in r:
        if (
            loc["Address"]["CountryCode"] == "United States"
            or loc["Address"]["CountryCode"] == "Canada"
        ):
            try:
                location_name = loc["Name"]
            except:
                location_name = "<MISSING>"
            try:
                street_address = loc["Address"]["Street"]
            except:
                street_address = "<MISSING>"
            try:
                city = loc["Address"]["City"]
            except:
                city = "<MISSING>"
            try:
                state = loc["Address"]["StateCode"]
            except:
                state = "<MISSING>"
            try:
                zipp = loc["Address"]["Zip"]
            except:
                zipp = "<MISSING>"
            try:
                if loc["Address"]["CountryCode"] == "United States":
                    country_code = "US"
                else:
                    country_code = "CA"
            except:
                country_code = "<MISSING>"
            try:
                store_number = str(loc["DCSId"])
            except:
                store_number = "<MISSING>"
            try:
                if loc["PhoneNumber"] == "-":
                    phone = "<MISSING>"
                else:
                    phone = loc["PhoneNumber"]
            except:
                phone = "<MISSING>"
            try:
                latitude = loc["Address"]["Latitude"]
            except:
                latitude = "<MISSING>"
            try:
                longitude = loc["Address"]["Longitude"]
            except:
                longitude = "<MISSING>"
            try:
                hours_of_operation = " ".join(loc["OpeningHours"]).replace(
                    "不营业", "closed"
                )
            except:
                hours_of_operation = "<MISSING>"
            try:
                page_url = "https://www.astonmartin.com" + loc["DealerPageUrl"]
            except:
                page_url = "<MISSING>"
            if "Aston Martin Long Island" in location_name:
                city = "ROSLYN"
                state = "New York"
                zipp = "11576"
            if "Aston Martin Denver" in location_name:
                state = "Colorado"
                zipp = "80129"
            store = []
            store.append("https://www.astonmartin.com")
            store.append(location_name if location_name else "<MISSING>")
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append(country_code if country_code else "<MISSING>")
            store.append(store_number if store_number else "<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("astonmartin")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(
                hours_of_operation if hours_of_operation.strip() else "<MISSING>"
            )
            store.append(page_url if page_url.strip() else "<MISSING>")
            store = [x.replace("é", "e") if isinstance(x, str) else x for x in store]
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
