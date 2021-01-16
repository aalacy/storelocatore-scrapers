import csv
import json

from lxml import etree

from sgrequests import SgRequests

import usaddress


base_url = "https://rockytopstores.com"


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


def parse_address(address):
    address = usaddress.parse(address)
    street = ""
    city = ""
    state = ""
    zipcode = ""
    for addr in address:
        if addr[1] == "PlaceName":
            city += addr[0].replace(",", "") + " "
        elif addr[1] == "ZipCode":
            zipcode = addr[0].replace(",", "")
        elif addr[1] == "StateName":
            state = addr[0].replace(",", "")
        else:
            street += addr[0].replace(",", "") + " "
    return {
        "street": get_value(street),
        "city": get_value(city),
        "state": get_value(state),
        "zipcode": get_value(zipcode),
    }


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
    url = "https://rockytopstores.com/locations?searchzip=Tennessee&task=search&radius=-1&option=com_mymaplocations&limit=0&component=com_mymaplocations&Itemid=223&zoom=9&format=json&geo=&limitstart=0&latitude=&longitude="
    session = SgRequests()

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    request = session.get(url, headers=headers)
    store_list = json.loads(request.text)["features"]
    for store in store_list:
        output = []
        output.append(base_url)  # url
        output.append(get_value(store["properties"]["name"]))  # location name
        address = ", ".join(
            eliminate_space(
                etree.HTML(store["properties"]["fulladdress"]).xpath(".//text()")
            )[:-2]
        ).replace("United States", "")
        address = parse_address(address)
        output.append(address["street"])  # address
        if address["state"] != "<MISSING>":
            output.append(address["city"])  # city
            output.append(address["state"])  # state
        else:
            output.append(validate(address["city"].split(" ")[:-1]))  # city
            output.append(validate(address["city"].split(" ")[-1]))  # state
        output.append(address["zipcode"])  # zipcode
        output.append("US")  # country code
        output.append(get_value(store["id"]))  # store_number
        output.append("<MISSING>")  # phone
        output.append("<MISSING>")  # location type
        output.append(get_value(store["geometry"]["coordinates"][0]))  # latitude
        output.append(get_value(store["geometry"]["coordinates"][1]))  # longitude
        output.append("<MISSING>")  # opening hours
        output.append(
            "https://rockytopstores.com" + get_value(store["properties"]["url"])
        )
        output_list.append(output)
    return output_list


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
