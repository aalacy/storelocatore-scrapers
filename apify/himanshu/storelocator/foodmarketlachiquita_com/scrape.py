import csv
import json

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
    base_url = "https://foodmarketlachiquita.com/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=448c203d5b&load_all=1&layout=1"
    r = session.get(base_url)
    data = r.json()
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://foodmarketlachiquita.com")
        store.append(store_data["title"])
        store.append(store_data["street"])
        store.append(store_data["city"])
        store.append(store_data["state"])
        if len(store_data["postal_code"].strip().split(" ")) == 2:
            store.append(store_data["postal_code"].strip().split(" ")[-1])
        else:
            store.append(store_data["postal_code"].strip())
        store.append("US")
        store.append(store_data["id"])
        store.append(store_data["phone"] if store_data["phone"] != "" else "<MISSING>")
        store.append("<MISSING>")
        store.append(store_data["lat"])
        store.append(store_data["lng"])
        hours = ""
        store_hours = json.loads(store_data["open_hours"])
        for key in store_hours:
            if store_hours[key] == "1":
                hours = hours + key + " 24/7 "
            else:
                hours = hours + key + " " + " ".join(store_hours[key]) + " "
        if hours == "":
            hours = "<MISSING>"
        store.append(hours)
        store.append("https://foodmarketlachiquita.com/locations/")
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
