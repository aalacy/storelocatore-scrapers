import csv

from sgrequests import SgRequests

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
    return_main_object = []
    data = session.get(
        "https://mallmotion.com:3033/api/v1/malllist?checking=true&device_type=web&lang_id=en&type=ONLYMALL"
    ).json()

    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://elsupermarkets.com")
        store.append(store_data["name"])
        store.append(store_data["address"])
        store.append(store_data["city"])
        store.append(store_data["state"])
        store.append(store_data["zip"])
        store.append("US")
        store.append(store_data["id"])
        store.append(store_data["phone_no"])
        store.append("<MISSING>")
        store.append(store_data["latitude"])
        store.append(store_data["longitude"])
        hours = ""
        if store_data["monday_start"] != "":
            hours = (
                hours
                + " monday "
                + store_data["monday_start"]
                + "-"
                + store_data["monday_end"]
                + " "
            )
        if store_data["tuesday_start"] and store_data["tuesday_start"] != "":
            hours = (
                hours
                + "tuesday "
                + store_data["tuesday_start"]
                + "-"
                + store_data["tuesday_end"]
                + " "
            )
        if store_data["wednesday_start"] and store_data["wednesday_start"] != "":
            hours = (
                hours
                + "wednesday "
                + store_data["wednesday_start"]
                + "-"
                + store_data["wednesday_end"]
                + " "
            )
        if store_data["thursday_start"] and store_data["thursday_start"] != "":
            hours = (
                hours
                + "thursday "
                + store_data["thursday_start"]
                + "-"
                + store_data["thursday_end"]
                + " "
            )
        if store_data["friday_start"] and store_data["friday_start"] != "":
            hours = (
                hours
                + "friday "
                + store_data["friday_start"]
                + "-"
                + store_data["friday_end"]
                + " "
            )
        if store_data["saturday_start"] and store_data["saturday_start"] != "":
            hours = (
                hours
                + "saturday "
                + store_data["saturday_start"]
                + "-"
                + store_data["saturday_end"]
                + " "
            )
        if store_data["sunday_start"] and store_data["sunday_start"] != "":
            hours = (
                hours
                + "sunday "
                + store_data["sunday_start"]
                + "-"
                + store_data["sunday_end"]
                + " "
            )
        if hours == "":
            hours = "<MISSING>"
        store.append(hours.strip() if hours != "" or hours is not None else "<MISSING>")
        store.append("https://elsupermarkets.com/store-locator")

        if store_data["state"] == "WB":
            continue
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
