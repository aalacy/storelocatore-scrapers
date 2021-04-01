import csv
from sgrequests import SgRequests
from lxml import etree

from sgscrape.sgpostal import parse_address_usa


base_url = "http://asianfoodmarkets.com"


def validate(item):
    if type(item) == list:
        item = " ".join(item)
    return item.replace("\r", "").replace("\t", "").replace("\n", "").strip()


def get_value(item):
    if not item:
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
    address = parse_address_usa(address)
    street = address.street_address_1
    if address.street_address_2:
        street += " " + address.street_address_2
    city = address.city
    state = address.state
    zipcode = address.postcode
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
                "page_url",
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
            ]
        )
        for row in data:
            writer.writerow(row)


def fetch_data():
    session = SgRequests()

    items = []

    start_url = "http://asianfoodmarkets.com"
    domain = "asianfoodmarkets.com"

    response = session.get(start_url)
    source = response.text
    store_list = (
        validate(
            source.split("var infoWindowContent = [")[1].split("// Display multiple")[0]
        )
        .replace("'", "")
        .replace("+", "")[1:-3]
        .split("],[")
    )
    geo_list = validate(source.split("var markers = [")[1].split("];")[0])[1:-1].split(
        "],["
    )
    for idx, store in enumerate(store_list):
        store = eliminate_space(etree.HTML(store).xpath(".//text()"))
        store_url = start_url
        location_name = store[0]
        address = parse_address(store[1])
        if "Online shopping" in store[1]:
            address = parse_address(store[2])
        street_address = address["street"]
        city = address["city"]
        state = address["state"]
        zip_code = address["zipcode"]
        country_code = "US"
        store_number = "<MISSING>"
        phone = [e.split(":")[-1].strip() for e in store if "Tel:" in e]
        phone = phone[0] if phone else "<MISSING>"
        location_type = "Asian Grocery Stores"
        geo = eliminate_space(geo_list[idx].split(","))
        latitude = geo[1]
        longitude = geo[2].replace("]", "")
        hours = [e.strip() for e in store if "AM-" in e]
        hours_of_operation = " ".join(hours) if hours else "<MISSING>"

        item = [
            domain,
            store_url,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
