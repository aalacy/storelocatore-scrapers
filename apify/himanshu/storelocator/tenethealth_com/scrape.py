import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("tenethealth_com")


session = SgRequests()


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
    r = session.get("https://www.tenethealth.com/api/facilities/GetFacilities").json()

    addressesess = []
    CountryCode = "US"
    for anchor in r["Facilities"]:
        location_name = anchor["Title"]
        page_url = anchor["WebsiteUrl"]
        if "CountryCode" in anchor:
            if anchor["CountryCode"] != "US" or anchor["CountryCode"] != "CA":
                continue
        street_address = anchor["Address"]["Street"]
        if "http" in street_address:
            street_address = "<MISSING>"
        if street_address.endswith(","):
            street_address = street_address[:-1]
        city = anchor["Address"]["City"]
        state = anchor["Address"]["StateCode"]
        zipp = anchor["Address"]["Zip"].strip()
        if len(zipp) == 2:
            zipp = "<MISSING>"
        phone = anchor["PhoneNumber"]
        if "FacilityClassName" in anchor:
            location_type = anchor["FacilityClassName"]
        else:
            location_type = "<MISSING>"
        latitude = anchor["Address"]["Latitude"]
        longitude = anchor["Address"]["Longitude"]
        store = []
        store.append("tenethealth.com")
        store.append(page_url)
        store.append(location_name)
        store.append(street_address.replace("�", ""))
        store.append(city)
        store.append(state)
        store.append(zipp if zipp else "<MISSING>")
        store.append(CountryCode)
        store.append("<MISSING>")
        store.append(phone)
        store.append(location_type)
        store.append(latitude)
        store.append(longitude)
        store.append("<MISSING>")
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        check = f"{store[2]} {store[3]}"
        if check in addressesess:
            continue
        addressesess.append(check)
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
