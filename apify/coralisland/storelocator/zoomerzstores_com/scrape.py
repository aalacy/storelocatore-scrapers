import csv
from lxml import etree
import usaddress
from sgrequests import SgRequests

session = SgRequests()
base_url = "https://zoomerzstores.com"


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
    output_list = []
    url = "https://zoomerzstores.com/locations?radius=-1&filter_catid=0&limit=0&filter_order=distance"

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": "32edeb25dad71c1c7dc8fbebd9de5d86=590499051483b07550207aad0c0b1b80; nrid=69257523a762df8d",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    formdata = {
        "searchzip": "los angeles",
        "task": "search",
        "radius": "-1",
        "option": "com_mymaplocations",
        "limit": "0",
        "component": "com_mymaplocations",
        "Itemid": "223",
        "zoom": "9",
        "format": "json",
        "geo": "",
        "limitstart": "0",
        "latitude": "",
        "longitude": "",
    }
    store_list = session.post(url, headers=headers, data=formdata).json()["features"]

    for store in store_list:
        output = []
        output.append(base_url)
        output.append("https://zoomerzstores.com" + store["properties"]["url"])
        output.append(get_value(store["properties"]["name"]))
        address = ", ".join(
            eliminate_space(
                etree.HTML(store["properties"]["fulladdress"]).xpath(".//text()")
            )[:-2]
        ).replace("United States", "")
        address = parse_address(address)
        output.append(address["street"])
        if address["state"] != "<MISSING>":
            output.append(address["city"])
            output.append(address["state"])
        else:
            output.append(validate(address["city"].split(" ")[:-1]))
            output.append(validate(address["city"].split(" ")[-1]))
        output.append(address["zipcode"])
        output.append("US")
        output.append(get_value(store["id"]))
        output.append("<MISSING>")
        output.append("Zoomerz Stores")
        output.append(get_value(store["geometry"]["coordinates"][0]))
        output.append(get_value(store["geometry"]["coordinates"][1]))
        output.append("<MISSING>")
        output_list.append(output)
    return output_list


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
