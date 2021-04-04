import csv
import json

from lxml import etree

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("zultimate_com")


base_url = "http://zultimate.com"


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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    output_list = []
    url = "http://zultimate.com/locations"
    session = SgRequests()
    source = session.get(url, headers=headers).text
    response = etree.HTML(source)
    link_list = response.xpath('//div[@class="wpseo-location"]/h3/a/@href')
    list_data = response.xpath('//div[@class="wpseo-location"]')

    for i, link in enumerate(link_list):
        logger.info(link)
        store_num = link.split("=")[-1]
        if not store_num.isnumeric():
            store_num = "<MISSING>"
        data = etree.HTML(session.get(link).text)
        store = json.loads(
            validate(data.xpath('.//script[@class="yoast-schema-graph"]//text()'))
        )["@graph"]
        location_name = get_value(store[-1]["name"])
        data_loc_name = (
            list_data[i].xpath('.//*[@class="wpseo-business-name"]//text()')[0].strip()
        )

        if location_name == data_loc_name:
            output = []
            output.append("zultimate.com")  # locator_domain
            output.append(link)  # url
            output.append(location_name)  # location name
            if len(store) > 3:
                for row in store:
                    if row["@type"] == "Place":
                        store = row
                        output.append(
                            get_value(store["address"]["streetAddress"])
                        )  # address
                        output.append(
                            get_value(store["address"]["addressLocality"])
                        )  # city
                        output.append(
                            get_value(store["address"]["addressRegion"]).replace(
                                " - California", ""
                            )
                        )  # state
                        output.append(
                            get_value(store["address"]["postalCode"])
                        )  # zipcode
                        output.append("US")  # country code
                        output.append(store_num)  # store_number
                        output.append(get_value(store["telephone"]))  # phone
                        output.append("<MISSING>")  # location type
                        output.append(get_value(store["geo"]["latitude"]))  # latitude
                        output.append(get_value(store["geo"]["longitude"]))  # longitude
                        store_hours = []
                        if store["openingHoursSpecification"]:
                            for hour in store["openingHoursSpecification"]:
                                for day in hour["dayOfWeek"]:
                                    store_hours.append(
                                        day + " " + hour["opens"] + "-" + hour["closes"]
                                    )
                        output.append(get_value(store_hours))  # opening hours
                        break
        else:
            data = list_data[i]

            output = []
            output.append("zultimate.com")  # locator_domain
            output.append(url)  # url
            output.append(data_loc_name)  # location name
            output.append(
                data.xpath('.//*[@class="street-address"]//text()')[0].strip()
            )  # address
            output.append(
                data.xpath('.//*[@class="locality"]//text()')[0].strip()
            )  # city
            output.append(
                data.xpath('.//*[@class="region"]//text()')[0].strip()
            )  # state
            output.append(
                data.xpath('.//*[@class="postal-code"]//text()')[0].strip()
            )  # zipcode
            output.append("US")  # country code
            output.append("<MISSING>")  # store_number
            output.append(
                data.xpath('.//*[@class="wpseo-phone"]//a//text()')[0].strip()
            )  # phone
            output.append("<MISSING>")  # location type
            output.append("<MISSING>")  # latitude
            output.append("<MISSING>")  # longitude
            output.append("<MISSING>")  # opening hours
        output_list.append(output)
    return output_list


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
