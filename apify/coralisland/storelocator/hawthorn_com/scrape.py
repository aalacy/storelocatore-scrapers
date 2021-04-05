import csv

from lxml import etree

from sglogging import SgLogSetup

from sgrequests import SgRequests

import usaddress

logger = SgLogSetup().get_logger("hawthorn_com")


base_url = "https://www.wyndhamhotels.com"


def validate(item):
    if type(item) == list:
        item = " ".join(item)
    while True:
        if item[-1:] == " ":
            item = item[:-1]
        else:
            break
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


def parse_address(address):
    address = usaddress.parse(address)
    street = ""
    city = ""
    state = ""
    zipcode = ""
    country = ""
    for addr in address:
        if addr[1] == "PlaceName":
            city += addr[0].replace(",", "") + " "
        elif addr[1] == "ZipCode":
            zipcode = addr[0].replace(",", "")
        elif addr[1] == "StateName":
            state = addr[0].replace(",", "")
        elif addr[1] == "CountryName":
            country = addr[0].replace(",", "")
        else:
            street += addr[0].replace(",", "") + " "

    return {
        "street": get_value(street),
        "city": get_value(city),
        "state": get_value(state),
        "zipcode": get_value(zipcode),
        "country": get_value(country),
    }


def fetch_data():
    output_list = []
    url = "https://www.wyndhamhotels.com/hawthorn-extended-stay/locations"
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "cookie": 'T2saVa1=A9afOJJsAQAAhTep2cwuVSxSAwi3CvH9xsP1ybzxJAJE7T7ZayUGw9X6TLGYAW5KyKGucn01wH8AAEB3AAAAAA==; userPreferredLanguage=en-ca; device_type=desktop; country_code=US; AKA_A2=A; firstReferringBrand=microtel; AWSELB=B3C98325144F5FE8D290FAD73119DBB01C2AEFCED73E565F3788222E78B310189A08519C02551A67524A7F9984486D38C0D76319318AD8D0EA744264411EEE9FC5BC72AD22; loglocale={"seed":"39a3ed10-187c-4646-aba8-a1f063ae45f2","pageHashCode":"7b92dcf9756003de838b8cce04566edc","timestamp":1569087148583,"channel":"responsive","serviceVersion":"1.0","language":"en-us"}; firstSearchBrand=microtel',
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
    }
    session = SgRequests()
    request = session.get(url, headers=headers)
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[@class="aem-rendered-content"]')[0].xpath(
        './/div[@class="state-container"]//li[@class="property"]'
    )
    for detail_url in store_list:
        session = SgRequests()
        detail_url = validate(detail_url.xpath(".//a")[0].xpath("./@href"))
        link = "https://www.wyndhamhotels.com" + detail_url
        detail_request = session.get(link)
        detail = etree.HTML(detail_request.text)

        address = validate(
            detail.xpath('.//div[contains(@class, "property-address")]//text()')
        )
        address = parse_address(address)

        try:
            phone = validate(
                detail.xpath('.//div[contains(@class, "property-phone")]')[0].xpath(
                    ".//text()"
                )
            ).replace("-", "")
        except:
            continue

        store_id = validate(
            detail_request.text.split('var overview_propertyId = "')[1].split('"')[0]
        )

        maps_url = detail.xpath('//a[@class="property-address-mobile"]')[0].attrib[
            "href"
        ]
        lat_lng = maps_url.split("&daddr=")[1].split("&", 1)[0]
        latitude = lat_lng.split(",")[0]
        longitude = lat_lng.split(",")[1]
        title = detail.xpath('//h1[contains(@class, "property-name")]/span/text()')[0]
        logger.info(title)
        country_code = "US"
        hours = "24 hours open"

        output = []
        output.append(base_url)  # url
        output.append(title)  # location name
        output.append(address["street"])  # address
        output.append(address["city"])  # city
        output.append(address["state"])  # state
        output.append(address["zipcode"])  # zipcode
        output.append(country_code)  # country code
        output.append(store_id)  # store_number
        output.append(phone)  # phone
        output.append("<MISSING>")  # location type
        output.append(latitude)  # latitude
        output.append(longitude)  # longitude
        output.append(hours)  # opening hours
        output.append(link)  # page_url
        output_list.append(output)

    return output_list


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
