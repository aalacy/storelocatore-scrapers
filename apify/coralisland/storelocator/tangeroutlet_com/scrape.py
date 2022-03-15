import csv

from lxml import etree

from sgrequests import SgRequests

import usaddress

base_url = "https://www.tangeroutlet.com"


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
    url = "https://www.tangeroutlet.com/locations"
    session = SgRequests()
    source = session.get(url).text
    response = etree.HTML(source)
    store_list = response.xpath('//div[contains(@class, "center-info-block")]')
    for store in store_list:
        output = []
        output.append(base_url)  # url
        output.append(validate(store.xpath(".//h3//text()")))  # location name
        address = eliminate_space(store.xpath('.//span[@class="address"]//text()'))
        output.append(address[0])  # address
        output.append(address[1].replace("ton, DC", "ton DC").split(",")[0])  # city
        statezip = eliminate_space(
            address[1].replace("ton, DC", "ton DC").split(",")[1].split(" ")
        )
        output.append(statezip[0])  # state
        output.append(validate(statezip[1:]))  # zipcode
        if len(statezip) == 3:
            output.append("CA")  # country code
        else:
            output.append("US")  # country code
        output.append("<MISSING>")  # store_number
        link = (
            "https://www.tangeroutlet.com/"
            + store.xpath('.//div[@class="centerLocation"]/a/@title')[0]
            + "/location"
        )
        page_data = etree.HTML(session.get(link).text)
        output.append(
            validate(page_data.xpath('.//div[@class="centerLocation"]/span/text()')[2])
        )  # phone
        output.append("<MISSING>")  # location type
        output.append(store.xpath("@data-latitude")[0])  # latitude
        output.append(store.xpath("@data-longitude")[0])  # longitude
        hour_list = page_data.xpath('//div[@class="hours-box"]//div[@class="capsule"]')
        store_hours = []
        for hour in hour_list:
            store_hours.append(
                validate(hour.xpath('.//div[@class="dotw"]//text()'))
                + " "
                + validate(hour.xpath('.//div[@class="hours "]//text()'))
            )
        output.append(get_value(", ".join(store_hours)))  # opening hours
        output.append(link)
        output_list.append(output)
    return output_list


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
