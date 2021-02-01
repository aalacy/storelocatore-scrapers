import csv
import json

from sgrequests import SgRequests

base_url = "https://www.joejuice.com"


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
    output_list = []
    url = "https://storerocket.global.ssl.fastly.net/api/user/KDB8e7W49M/locations"
    session = SgRequests()
    request = session.get(url)
    store_list = json.loads(request.text)["results"]["locations"]
    for store in store_list:
        output = []
        if get_value(store["country"]).lower() in ["united states", "united kingdom"]:
            output.append(base_url)  # url
            output.append(get_value(store["name"]))  # location name
            output.append(
                get_value(
                    store["address_line_1"] + " " + store["address_line_2"]
                ).replace(" NY", "")
            )  # address
            output.append(get_value(store["city"]))  # city
            output.append(get_value(store["state"]))  # state
            output.append(get_value(store["postcode"]))  # zipcode
            output.append(get_value(store["country"]))  # country code
            output.append(get_value(store["id"]))  # store_number
            output.append(get_value(store["phone"]))  # phone
            output.append("<MISSING>")  # location type
            output.append(get_value(store["lat"]))  # latitude
            output.append(get_value(store["lng"]))  # longitude
            store_hours = []
            if store["hours"]:
                for day, hour in list(store["hours"].items()):
                    hour = validate(hour)
                    if hour == "":
                        hour = "closed"
                    store_hours.append(day + " " + hour)
            else:
                store_hours = "<MISSING>"
            output.append(get_value(store_hours))  # opening hours
            output.append("https://www.joejuice.com/stores")
            output_list.append(output)
    return output_list


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
