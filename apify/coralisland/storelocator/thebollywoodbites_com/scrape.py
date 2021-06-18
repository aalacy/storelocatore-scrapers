import csv

from lxml import etree

from sgrequests import SgRequests

base_url = "https://www.thebollywoodbites.com"


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
    output_list = []
    url = "https://www.thebollywoodbites.com/contact-us/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    source = session.get(url, headers=headers).text
    response = etree.HTML(source)
    store_list = response.xpath(
        '//div[@class="wpb_column vc_column_container vc_col-sm-6"]'
    )
    for store in store_list:
        geo_loc = (
            validate(store.xpath('.//div[@class="wpb_map_wraper"]//iframe/@src'))
            .split("!2d")[1]
            .split("!3m")[0]
            .split("!3d")
        )
        store = eliminate_space(store.xpath(".//text()"))
        output = []
        output.append(base_url)  # url
        output.append(url)  # page url
        address = store[1].strip().split(",")
        output.append(address[0])  # location name
        output.append(get_value(address[1]))  # address
        output.append(address[2])  # city
        output.append(address[3].strip().split("-")[0].strip())  # state
        output.append(address[3].strip().split("-")[1])  # zipcode
        output.append("US")  # country code
        output.append("<MISSING>")  # store_number
        output.append(store[-1])  # phone
        output.append("<MISSING>")  # location type
        output.append(geo_loc[1])  # latitude
        output.append(geo_loc[0])  # longitude
        output.append("<MISSING>")  # opening hours
        output_list.append(output)
    return output_list


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
