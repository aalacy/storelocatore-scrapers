import csv
from sgrequests import SgRequests
from lxml import etree

base_url = "https://www.grifolsplasma.com"


def validate(item):
    if not item:
        item = ""
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = " ".join(item)
    return item.strip()


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
    output_list = []
    url = "https://www.grifolsplasma.com/en/locations/find-a-donation-center"
    session = SgRequests()
    source = session.get(url).text
    response = etree.HTML(source)
    link_list = response.xpath('//div[@id="all-centers-grid-results"]//a/@href')
    for link in link_list:
        data = session.get(link).text
        store = etree.HTML(data)
        output = []
        output.append(link)  # page_url
        detail = eliminate_space(store.xpath('.//div[@class="center-address"]//text()'))
        if len(detail) > 3:
            if detail[-2] == "999":
                detail.pop(-2)
                detail.pop(-1)
                detail.append(detail[-1])

        if len(detail) > 0:
            output.append(base_url)  # url

            if len(detail) == 6:
                output.append(detail[0])  # location name
                output.append(detail[2])  # address
                try:
                    address = detail[3].strip().split(",")
                    output.append(address[0])  # city
                    output.append(address[1])  # state
                    output.append(address[2])  # zipcode
                except Exception:
                    try:
                        address = detail[2].strip().split(",")
                        output.append(address[0])  # city
                        output.append(address[1])  # state
                        output.append(address[2])  # zipcode
                    except Exception:
                        raise Exception

                output.append("US")  # country code
                output.append("<MISSING>")  # store_number
                output.append(detail[-1])  # phone
                output.append(
                    "Pride for Donors. Passion for Patients | GRIFOLS"
                )  # location type
                geo_loc = data.split(";f=")[1].split(";var")[0].split(";e=")
                output.append(geo_loc[0].replace("+", ""))  # latitude
                output.append(geo_loc[1])  # longitude
                store_hours = eliminate_space(
                    store.xpath('.//div[@class="center-column-2"]//p//text()')
                )
                output.append(get_value(store_hours))  # opening hours
            else:
                output.append(detail[0])  # location name
                output.append(detail[1])  # address
                address = detail[2].strip().split(",")
                output.append(address[0])  # city
                output.append(address[1])  # state
                output.append(address[2])  # zipcode
                output.append("US")  # country code
                output.append("<MISSING>")  # store_number
                output.append(detail[-1])  # phone
                output.append(
                    "Pride for Donors. Passion for Patients | GRIFOLS"
                )  # location type
                geo_loc = data.split(";f=")[1].split(";var")[0].split(";e=")
                output.append(geo_loc[0].replace("+", ""))  # latitude
                output.append(geo_loc[1])  # longitude
                store_hours = eliminate_space(
                    store.xpath('.//div[@class="center-column-2"]//p//text()')
                )
                output.append(get_value(store_hours))  # opening hours
            if output not in output_list:
                output_list.append(output)
    return output_list


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
