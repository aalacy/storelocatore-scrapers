import csv

from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_url = "https://www.vancleefarpels.com"
    base_link = "https://www.vancleefarpels.com/us/en/store-locator-results-page.stores-with-hours.json"

    data = session.get(base_link, headers=headers).json()
    for store_data in data:
        if "United States" in store_data["address"]["country"]:
            country = "US"
        elif "Canada" in store_data["address"]["country"]:
            country = "CA"
        else:
            continue

        store = []
        store.append("https://www.vancleefarpels.com")
        store.append(store_data["name"])
        store.append(store_data["address"]["street"])
        store.append(
            store_data["address"]["city"]
            if store_data["address"]["city"] != ""
            else "<MISSING>"
        )
        store.append(
            store_data["address"]["state"]
            if store_data["address"]["state"] != ""
            else "<MISSING>"
        )
        store.append(
            store_data["address"]["zipCode"]
            if store_data["address"]["zipCode"] != ""
            else "<MISSING>"
        )
        store.append(country)
        store.append(store_data["id"])
        store.append(store_data["phoneNumber"])
        store.append("<MISSING>")
        store.append(store_data["location"]["latitude"])
        store.append(store_data["location"]["longitude"])

        hours_of_operation = ""
        raw_hours = store_data["openingHours"]
        for raw_hour in raw_hours:
            hours_of_operation = (
                hours_of_operation
                + " "
                + raw_hours[raw_hour][0]["dayOfWeek"]
                + " "
                + raw_hours[raw_hour][0]["openingTime"]
                + "-"
                + raw_hours[raw_hour][0]["closingTime"]
            ).strip()

        store.append(hours_of_operation)
        store.append(base_url + store_data["pagePath"])
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
