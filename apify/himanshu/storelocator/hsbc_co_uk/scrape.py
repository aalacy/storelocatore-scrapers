import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("hsbc_co_uk")
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
    r = session.get("https://api.hsbc.com/open-banking/v2.2/atms").json()
    attr = r["data"][0]["Brand"][0]["ATM"]

    location_name = "<MISSING>"
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "<MISSING>"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    for data in attr:
        try:
            location_name = data["Location"]["Site"]["Name"]
        except:
            location_name = "<MISSING>"

        try:
            street_address = data["Location"]["PostalAddress"]["StreetName"]
        except:
            street_address = "<MISSING>"

        try:
            if data["Location"]["PostalAddress"]["TownName"] == "3":
                city = "<MISSING>"
            else:
                city = data["Location"]["PostalAddress"]["TownName"]
        except:
            city = "<MISSING>"

        state = "<MISSING>"
        try:
            zipp = data["Location"]["PostalAddress"]["PostCode"]
        except:
            zipp = "<MISSING>"

        try:
            country_code = data["Location"]["PostalAddress"]["Country"]
        except:
            country_code = "<MISSING>"

        store_number = "<MISSING>"
        phone = "<MISSING>"
        location_type = "ATM"
        try:
            latitude = data["Location"]["PostalAddress"]["GeoLocation"][
                "GeographicCoordinates"
            ]["Latitude"]
        except:
            latitude = "<MISSING>"

        try:
            longitude = data["Location"]["PostalAddress"]["GeoLocation"][
                "GeographicCoordinates"
            ]["Longitude"]
        except:
            longitude = "<MISSING>"

        hours_of_operation = "24 HOURS"
        page_url = "<MISSING>"

        store = []
        store.append("https://www.hsbc.co.uk")
        store.append(location_name if location_name else "<MISSING>")
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append(country_code if country_code else "<MISSING>")
        store.append(store_number if store_number else "<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append(location_type if location_type else "<MISSING>")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append(hours_of_operation if hours_of_operation.strip() else "<MISSING>")
        store.append(page_url if page_url.strip() else "<MISSING>")

        yield store

    r1 = session.get("https://api.hsbc.com/open-banking/v2.2/branches").json()
    attr1 = r1["data"][0]["Brand"][0]["Branch"]

    for data1 in attr1:

        try:
            location_name = data1["Name"]
        except:
            location_name = "<MISSING>"

        try:
            street_address = (
                data1["PostalAddress"]["BuildingNumber"]
                + " "
                + data1["PostalAddress"]["StreetName"]
            )
        except:
            street_address = "<MISSING>"

        try:
            city = data1["PostalAddress"]["TownName"]
        except:
            city = "<MISSING>"

        try:
            state = "<MISSING>"
        except:
            state = "<MISSING>"

        try:
            zipp = data1["PostalAddress"]["PostCode"]
        except:
            zipp = "<MISSING>"

        try:
            country_code = data1["PostalAddress"]["Country"]
        except:
            country_code = "<MISSING>"

        try:
            store_number = "<MISSING>"
        except:
            store_number = "<MISSING>"

        try:
            phone = data1["ContactInfo"][0]["ContactContent"]
        except:
            phone = "<MISSING>"

        try:
            location_type = data1["Type"] + " Branch"
        except:
            location_type = "<MISSING>"

        try:
            latitude = data1["PostalAddress"]["GeoLocation"]["GeographicCoordinates"][
                "Latitude"
            ]
        except:
            latitude = "<MISSING>"

        try:
            longitude = data1["PostalAddress"]["GeoLocation"]["GeographicCoordinates"][
                "Longitude"
            ]
        except:
            longitude = "<MISSING>"

        try:
            hours_of_operation = ""
            availability = data1["Availability"]["StandardAvailability"]["Day"]
            for week in availability:
                for time in week["OpeningHours"]:
                    hours_of_operation = (
                        hours_of_operation
                        + " "
                        + week["Name"]
                        + " OpeningTime "
                        + time["OpeningTime"]
                        + " ClosingTime "
                        + time["ClosingTime"]
                    )
        except:
            hours_of_operation = "<MISSING>"
        page_url = "<MISSING>"

        store = []
        store.append("https://www.hsbc.co.uk")
        store.append(location_name if location_name else "<MISSING>")
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append(country_code if country_code else "<MISSING>")
        store.append(store_number if store_number else "<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append(location_type if location_type else "<MISSING>")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append(hours_of_operation if hours_of_operation.strip() else "<MISSING>")
        store.append(page_url if page_url else "<MISSING>")

        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
