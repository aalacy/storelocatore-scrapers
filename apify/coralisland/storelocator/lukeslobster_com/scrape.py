import csv
import json

from sgrequests import SgRequests

base_url = "https://www.lukeslobster.com"


def validate(item):
    if item is None:
        item = ""
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = " ".join(item)
    return item.strip()


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
    url = "https://stockist.co/api/v1/u8944/locations/all.js?callback=_stockistAllStoresCallback"
    session = SgRequests()
    source = session.get(url).text
    store_list = json.loads(source.split("Callback(")[1].split(");")[0])
    for store in store_list:
        output = []
        output.append(base_url)  # url
        output.append(get_value(store["name"]))  # location name
        raw_address = store["full_address"].replace(", USA", "")
        if "japan" in raw_address.lower() or "singa" in raw_address.lower():
            continue
        output.append(get_value(",".join(raw_address.split(",")[:-2])))  # address
        output.append(get_value(raw_address.split(",")[-2]))  # city
        output.append(get_value(raw_address.split(",")[-1].split()[0]))  # state
        output.append(get_value(raw_address.split(",")[-1].split()[1]))  # zipcode
        output.append("US")  # country code
        output.append(get_value(store["id"]))  # store_number
        output.append(get_value(store["phone"]))  # phone
        location_type = "<MISSING>"
        store_hours = store["description"].replace("\n", "; ").strip()
        if "closed until further" in store_hours:
            store_hours = "<MISSING>"
            location_type = "Temporarily Closed"
        output.append(location_type)  # location type
        output.append(get_value(store["latitude"]))  # latitude
        output.append(get_value(store["longitude"]))  # longitude
        output.append(get_value(store_hours))  # opening hours
        output.append(store["website"])
        output_list.append(output)
    return output_list


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
