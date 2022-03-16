import csv
import json

from sgrequests import SgRequests

base_url = "https://www.maplefields.com"


def validate(item):
    if item is None:
        item = ""
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = " ".join(item)
    return item.replace("\u2013", "-").strip()


def get_value(item):
    if item is None:
        item = "<MISSING>"
    item = validate(item)
    if item == "":
        item = "<MISSING>"
    return item


def eliminate_space(items):
    rets = []
    for item in items:
        item = validate(item)
        if item != "":
            rets.append(item)
    return rets


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    output_list = []
    url = "https://www.maplefields.com/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=faa40a2fa2&load_all=1&layout=1"
    store_list = session.get(url, headers=headers).json()
    for store in store_list:
        output = []
        output.append(base_url)  # url
        output.append("https://maplefields.com/store-locator")  # page url
        output.append(get_value(store["title"]))  # location name
        output.append(get_value(store["street"]))  # address
        output.append(get_value(store["city"]))  # city
        output.append(get_value(store["state"]))  # state
        output.append(get_value(store["postal_code"]))  # zipcode
        output.append(get_value(store["country"]))  # country code
        output.append(get_value(store["id"]))  # store_number
        output.append(
            get_value(store["phone"].replace("Maplefields Swanton", ""))
        )  # phone
        output.append(
            get_value(
                store["description"].strip().replace("\r\n", ", ").replace("  ", " ")
            )
        )  # location type
        output.append(get_value(store["lat"]))  # latitude
        output.append(get_value(store["lng"]))  # longitude
        hours = json.loads(store["open_hours"])
        store_hours = []
        for key, hour in list(hours.items()):
            store_hours.append(key + " " + validate(hour))
        store_hours = get_value(store_hours)
        output.append(
            store_hours.replace(
                "mon 1 tue 1 wed 1 thu 1 fri 1 sat 1 sun 1", "<MISSING>"
            ).strip()
        )  # opening hours
        output_list.append(output)
    return output_list


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
