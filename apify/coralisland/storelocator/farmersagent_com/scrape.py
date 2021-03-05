import csv

from lxml import etree

from sglogging import sglog

from sgrequests import SgRequests

log = sglog.SgLogSetup().get_logger(logger_name="agents.farmers.com")

base_url = "https://agents.farmers.com"


def validate(item):
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


def parse_detail(store, link):
    output = []
    output.append(base_url)  # url
    output.append(link)  # url
    location_name = get_value(store.xpath('.//h1[@itemprop="name"]//text()'))
    output.append(location_name)  # location name
    street = validate(store.xpath('.//meta[@itemprop="streetAddress"]//@content')[0])
    output.append(get_value(street))  # address
    output.append(
        get_value(store.xpath('.//meta[@itemprop="addressLocality"]//@content')[0])
    )  # city
    output.append(
        get_value(store.xpath('.//abbr[@class="c-address-state"]//text()')[0].strip())
    )  # state
    output.append(
        get_value(
            store.xpath('.//span[@class="c-address-postal-code"]//text()')[0].strip()
        )
    )  # zipcode
    output.append("US")  # country code
    store_number = (
        store.xpath('.//script[@id="js-agent-id"]//text()')[0].replace('"', "").strip()
    )
    output.append(store_number)  # store_number
    output.append(
        get_value(store.xpath('.//span[@itemprop="telephone"]//text()')[0])
    )  # phone
    output.append("<MISSING>")  # location type
    geo = validate(store.xpath('.//meta[@name="geo.position"]//@content')).split(";")
    if len(geo) > 0:
        output.append(geo[0])  # latitude
        output.append(geo[1])  # longitude
    output.append(
        get_value(
            eliminate_space(
                store.xpath(
                    './/table[@class="c-location-hours-details"]//tbody//text()'
                )
            )
        )
    )  # opening hours
    return location_name + street, output


def fetch_data():
    output_list = []
    found = []
    url = "https://agents.farmers.com"
    session = SgRequests()

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    request = session.get(url, headers=headers)
    response = etree.HTML(request.text)
    state_list = response.xpath('//a[@class="Directory-listLink"]/@href')
    for state in state_list:
        state = url + "/" + state
        log.info(state)
        state_response = etree.HTML(session.get(state, headers=headers).text)
        if state_response is not None:
            city_list = state_response.xpath('//a[@class="Directory-listLink"]/@href')
            store_list = state_response.xpath('//a[@class="location-title-link"]/@href')
            if len(city_list) > 0:
                for city in city_list:
                    city = url + "/" + city
                    city_response = etree.HTML(session.get(city, headers=headers).text)
                    if city_response is not None:
                        store_list = city_response.xpath(
                            '//a[@class="location-title-link"]/@href'
                        )
                        if len(store_list) > 0:
                            for store in store_list:
                                store = url + store[2:]
                                store_response = etree.HTML(
                                    session.get(store, headers=headers).text
                                )
                                if store_response is not None:
                                    store_number, output = parse_detail(
                                        store_response, store
                                    )
                                    if store_number in found:
                                        continue
                                    found.append(store_number)
                                    output_list.append(output)
                        else:
                            store_number, output = parse_detail(city_response, city)
                            if store_number in found:
                                continue
                            found.append(store_number)
                            output_list.append(output)
            elif len(store_list) > 0:
                for store in store_list:
                    store = url + store[2:]
                    store_response = etree.HTML(
                        session.get(store, headers=headers).text
                    )
                    if store_response is not None:
                        store_number, output = parse_detail(store_response, store)
                        if store_number in found:
                            continue
                        found.append(store_number)
                        output_list.append(output)
            else:
                store_number, output = parse_detail(state_response, state)
                if store_number in found:
                    continue
                found.append(store_number)
                output_list.append(output)
    return output_list


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
