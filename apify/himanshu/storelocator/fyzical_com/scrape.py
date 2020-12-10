import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("fyzical_com")


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []

    data = session.get(
        "https://www.fyzical.com/contact.php?v=4&action=ajax_get_locations&ne=65.47336744902078,-12.629251250000006&sw=8.312726964373702,-167.66831375"
    ).json()

    for data in data["locations"]:
        Suite = ""
        Suit = ""
        if "Suite" in data:

            Suite = str(data["Suite"])
            if Suite:
                if "suite" in str(Suite).lower():
                    Suit = Suite
                else:
                    Suit = " Suite " + Suite

        street_address = data["Street"] + " " + Suit
        location_name = data["Name"]
        city = data["City"]
        zipp = data["Zip"]
        state = data["State"]
        phone = data["Phone"]
        longitude = data["Longitude"]
        latitude = data["Latitude"]
        page_url = data["Long_description_url"]

        hours = ""
        for hour in data["Workhours"]:
            if data["Workhours"][hour]["Always_closed"] == "yes":
                hours = hours + " " + data["Workhours"][hour]["Weekday"] + " Closed "
            else:
                hours = (
                    hours
                    + " "
                    + data["Workhours"][hour]["Weekday"]
                    + " "
                    + data["Workhours"][hour]["Opening_time"]
                    + " "
                    + data["Workhours"][hour]["Closing_time"]
                )

        store_number = "<MISSING>"
        store = []
        store.append("https://www.fyzical.com")
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append(store_number)
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append(hours)
        store.append(page_url if page_url else "<MISSING>")
        store = [
            str(x)
            .strip()
            .replace("0.000000", "<MISSING>")
            .replace("(248) 865-4148 / 4444", "(248) 865-4148")
            if x
            else "<MISSING>"
            for x in store
        ]
        if store[2] in addresses:
            continue
        addresses.append(store[2])

        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
