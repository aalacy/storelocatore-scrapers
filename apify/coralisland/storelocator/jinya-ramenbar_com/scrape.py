import csv
from sgrequests import SgRequests
from lxml import etree
import json
import usaddress
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("jinya-ramenbar_com")

base_url = "http://jinya-ramenbar.com"


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


def get_lat_lng_map(source):
    lat_lng_map = {}
    lat, lng = None, None
    for line in source.splitlines():
        if "lat: " in line:
            lat = line.split(":")[1].split(",")[0].strip()
        elif "lng: " in line:
            lng = line.split(":")[1].split(",")[0].strip()
        elif "url: " in line:
            url = line.split("'")[1]
            lat_lng_map[url] = (lat, lng)
    return lat_lng_map


def fetch_data():
    output_list = []
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36",
        "referer": "https://www.jinyaramenbar.com/locations/",
        "origin": "https://www.jinyaramenbar.com",
        "authority": "www.jinyaramenbar.com",
        "method": "POST",
        "path": "/cms/wp-content/themes/jinyaramenbar/geo-location.php",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    url = "https://www.jinyaramenbar.com/cms/wp-content/themes/jinyaramenbar/geo-location.php"
    session = SgRequests()
    source = session.post(
        url,
        headers=headers,
        data=json.dumps({"nowstate": "Cannot+get+current+location."}),
    ).text
    response = etree.HTML(source)
    store_links = [
        x.attrib["href"]
        for x in response.xpath(
            '//div[@class="content"]//a[contains(@href, "jinyaramenbar.com/locations")]'
        )
    ]
    for store_link in store_links:
        logger.info(store_link)
        if "coming-soon" in store_link:
            continue
        output = []
        store_source = session.get(store_link, headers=headers).text
        response = etree.HTML(store_source)
        lat_lng_map = get_lat_lng_map(store_source)
        title = validate(response.xpath("//article//h1//text()"))
        if "coming soon" in title.lower():
            continue
        output.append(base_url)  # locator_domain
        output.append(title)  # location name
        raw_details = response.xpath('//div[@class="loc_details"]')[0]
        details = [x.strip() for x in raw_details.itertext() if x.strip()]
        raw_address = details[0]
        if len(details) > 1:
            if len([x for x in details[1] if x.isdigit()]) < 10:
                raw_phone = "<MISSING>"
                raw_hours = ", ".join(details[1:])
            else:
                raw_phone = details[1]
                raw_hours = ", ".join(details[2:])
            if "/" in raw_phone:
                raw_phone = raw_phone.split("/")[0].strip()
        if "canada" not in raw_address.lower():
            address = parse_address(raw_address)
            output.append(address["street"])  # address
            output.append(address["city"])  # city
            output.append(address["state"])  # state
            output.append(address["zipcode"])  # zipcode
            output.append("US")  # country code
        else:
            address = eliminate_space(raw_address.replace("Canada", "").split(","))
            city = address[-2].split(" ")
            if len(city) < 2:
                output.append(get_value(address[:-2]))  # address
                output.append(get_value(address[-2]))  # city
            else:
                output.append(get_value(address[:-1]).replace(city[-1], ""))  # address
                output.append(city[-1])  # city
            output.append(get_value(address[-1][:-7]))  # state
            output.append(get_value(address[-1][-7:]))  # zipcode
            output.append("CA")  # country code
        output.append("<MISSING>")  # store_number
        output.append(get_value(raw_phone))  # phone
        output.append("<MISSING>")  # location type
        output.append(lat_lng_map.get(store_link, "<MISSING>")[0])  # latitude
        output.append(lat_lng_map.get(store_link, "<MISSING>")[1])  # longitude
        output.append(get_value(raw_hours))  # hours_of_operation
        output.append(store_link)  # page_url
        output_list.append(output)
    return output_list


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
