import csv
from sgrequests import SgRequests
from lxml import etree
import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup as BS


base_url = "https://www.marshfieldclinic.org"
log = sglog.SgLogSetup().get_logger(logger_name="marshfieldclinic_org")


def validate(item):
    if item is None:
        item = ""
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = " ".join(item)
    return (
        item.replace("\u2013", "-")
        .strip()
        .replace("\t", "")
        .replace("  ", "")
        .replace("\r\n", " ")
    )


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
            state = addr[0].replace(",", "") + " "
        else:
            street += addr[0].replace(",", "") + " "
    return {
        "street": get_value(street),
        "city": get_value(city),
        "state": get_value(state),
        "zipcode": get_value(zipcode),
    }


def write_output(data):
    with open(
        "data.csv", mode="w", newline="", encoding="utf-8", errors="replace"
    ) as output_file:
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
    url = "https://www.marshfieldclinic.org/locations"
    session = SgRequests(retry_behavior=None, proxy_rotation_failure_threshold=0)
    source = session.get(url).text
    response = etree.HTML(source)
    url_list = []
    loc_types = (
        response.xpath('//div[@id="UrgentCareList"]')
        + response.xpath('//div[@id="ClinicsList"]')
        + response.xpath('//div[@id="HospitalsList"]')
        + response.xpath('//ul[@class="blockLinks floatListCTALoc"]')
    )

    store_list = []
    for typ in loc_types:
        location_type = typ.xpath("ul/li[1]/span/text()")
        if len(location_type) > 0:
            location_type = location_type[0].strip()
        else:
            location_type = "Clinics & Medical Offices"

        temp_url_list = typ.xpath(".//a/@href")
        for temp in temp_url_list:
            store_list.append(
                temp.replace("https://www.marshfieldclinic.org", "").strip()
            )
        for store_link in store_list:
            if "#" in store_link or "http" in store_link:
                continue

            page_url = "https://www.marshfieldclinic.org" + store_link.lower()
            if page_url in url_list:
                continue
            url_list.append(page_url)
            page_res = session.get(page_url)

            if base_url not in page_res.url:
                log.info(
                    f"URL REDIRECTED (to new domain and IGNORED)!!!\n {page_url} ---> {page_res.url}\n----------\n"
                )
                continue
            store = etree.HTML(page_res.text)
            output = []
            output.append(base_url)  # url
            output.append(validate(page_url))  # page url
            log.info(page_url)
            name = store.xpath('.//span[@id="loctitle"]//text()')
            if len(name) > 0:
                output.append("".join(name[0]).strip())  # location name
                address = eliminate_space(
                    store.xpath('.//div[@class="contentDetail"]//h2')[1].xpath(
                        "./text()"
                    )
                )
                address = parse_address(", ".join(address))
                output.append(address["street"])  # address
                output.append(address["city"])  # city
                output.append(address["state"])  # state
                output.append(address["zipcode"])  # zipcode
                output.append("US")  # country code
                output.append("<MISSING>")  # store_number
                phone = store.xpath('.//h2[@id="PhoneTextHeading"]/a/text()')
                if len(phone) <= 0:
                    phone = store.xpath('.//h2[@id="PhoneTextHeading"]/text()')
                output.append(get_value(phone).replace("Phone:", "").strip())  # phone
                output.append(location_type)  # location type
                output.append(
                    get_value(store.xpath('.//span[@id="latitude"]//text()')[0])
                )  # latitude
                output.append(
                    get_value(store.xpath('.//span[@id="longitude"]//text()')[0])
                )  # longitude
                store_hours = "; ".join(
                    get_value(
                        eliminate_space(
                            store.xpath('.//span[@id="officehours"]//text()')
                        )
                    ).split("\n")
                ).strip()

                store_hours = BS(store_hours, "html.parser").get_text()
                if len(store_hours) <= 0:
                    hours = store.xpath('//ul[@style="list-style-type: disc;"]//text()')
                    hours_list = []
                    for hour in hours:
                        if len("".join(hour).strip()) > 0:
                            hours_list.append("".join(hour).strip())

                    store_hours = "; ".join(hours_list).strip()
                if len(store_hours) <= 0:
                    store_hours = "<MISSING>"
                output.append(store_hours)  # opening hours
                yield output
            else:
                name = store.xpath('.//div[@class="hero-caption-content"]//h3//text()')

                if len(name) <= 0:
                    continue
                output.append("".join(name[0]).strip())  # location name
                details = eliminate_space(
                    store.xpath('.//div[@class="foot-content-3 clearfix"]//p//text()')
                )
                address = parse_address(", ".join(details[1:-1]))
                output.append(address["street"])  # address
                output.append(address["city"])  # city
                output.append(address["state"])  # state
                output.append(address["zipcode"])  # zipcode
                output.append("US")  # country code
                output.append("<MISSING>")  # store_number
                output.append(get_value(details[-1]).replace("Phone:", ""))  # phone
                output.append(location_type)  # location type
                output.append(
                    get_value(store.xpath('.//span[@id="latitude"]//text()'))
                )  # latitude
                output.append(
                    get_value(store.xpath('.//span[@id="longitude"]//text()'))
                )  # longitude
                store_hours = "; ".join(
                    get_value(
                        eliminate_space(
                            store.xpath('.//div[@class="span9"]//p')[1].xpath(
                                ".//text()"
                            )
                        )
                    ).split("\n")
                ).strip()
                output.append(store_hours)  # opening hours
                store_hours = BS(store_hours, "html.parser").get_text()
                yield output


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
