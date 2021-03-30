import csv
import json

from lxml import etree

from sgrequests import SgRequests

base_url = "https://yourpie.com"


def validate(item):
    if type(item) == list:
        item = " ".join(item)
    return item.strip()


def get_value(item):
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
    url = "https://yourpie.com/wp-admin/admin-ajax.php?action=store_search&max_results=10000&search_radius=20002000&autoload=1"
    session = SgRequests()
    request = session.get(url)
    store_list = json.loads(request.text)
    for store in store_list:
        if "Coming Soon" in get_value(store["store"]) or store["coming_soon"].strip():
            continue
        hours = store.get("hours")
        if hours:
            store_hours = get_value(etree.HTML(hours).xpath(".//text()"))
        else:
            store_hours = "<MISSING>"
        output = []
        output.append(base_url)  # url
        output.append(
            get_value(store["store"]).replace("&#8211;", "-").replace("&#8217;", "'")
        )  # location name
        output.append(get_value(store["address"]))  # address
        output.append(get_value(store["city"]))  # city
        output.append(get_value(store["state"]))  # state
        output.append(get_value(store["zip"]))  # zipcode
        output.append("US")  # country code
        output.append(store["id"])  # store_number
        output.append(get_value(store["phone"]))  # phone
        output.append("<MISSING>")  # location type
        output.append(store["lat"])  # latitude
        output.append(store["lng"])  # longitude
        output.append(store_hours)  # opening hours
        output.append(store["permalink"])  # page_url
        output_list.append(output)
    return output_list


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
