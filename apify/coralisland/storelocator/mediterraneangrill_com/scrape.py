import csv

from lxml import etree

from sgrequests import SgRequests

base_url = "https://www.mediterraneangrill.com"


def validate(item):
    if item is None:
        item = ""
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = " ".join(item)
    return item.strip("\u200b").strip()


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

        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    output_list = []
    url = "https://www.mediterraneangrill.com/locations"
    session = SgRequests()
    source = session.get(url).text
    response = etree.HTML(source)
    store_list = response.xpath(
        '//div[@data-mesh-id="SITE_FOOTERinlineContent-gridContainer"]//div'
    )
    address_list = eliminate_space(store_list[0].xpath('.//p[@class="font_8"]//text()'))
    phone_list = eliminate_space(store_list[1].xpath('.//p[@class="font_8"]//text()'))
    store_hours = validate(eliminate_space(store_list[2].xpath(".//text()"))[1:])
    for idx, address in enumerate(address_list):
        output = []
        address = address.split(",")
        output.append(base_url)  # domain
        output.append(url)  # url
        output.append(address[1].strip())  # location name
        output.append(address[0].strip())  # address
        output.append(address[1].strip())  # city
        output.append(address[2].strip())  # state
        output.append(address[3].strip())  # zipcode
        output.append("US")  # country code
        output.append("<MISSING>")  # store_number
        output.append(phone_list[idx].split(":")[-1].strip())  # phone
        output.append("<MISSING>")  # location type
        output.append("<INACCESSIBLE>")  # latitude
        output.append("<INACCESSIBLE>")  # longitude
        output.append(store_hours)  # opening hours
        output_list.append(output)
    return output_list


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
