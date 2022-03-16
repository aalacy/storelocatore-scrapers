import time
import csv
import usaddress
from lxml import html
from webdriver_manager.chrome import ChromeDriverManager
from sgselenium import SgChrome
from sglogging import sglog
import ssl

locator_domain = "usainsuranceco.net"
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)

ssl._create_default_https_context = ssl._create_unverified_context

user_agent = (
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
)

driver = SgChrome(
    is_headless=True,
    user_agent=user_agent,
    executable_path=ChromeDriverManager().install(),
).driver()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
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


def get_address(line):
    tag = {
        "Recipient": "recipient",
        "AddressNumber": "address1",
        "AddressNumberPrefix": "address1",
        "AddressNumberSuffix": "address1",
        "StreetName": "address1",
        "StreetNamePreDirectional": "address1",
        "StreetNamePreModifier": "address1",
        "StreetNamePreType": "address1",
        "StreetNamePostDirectional": "address1",
        "StreetNamePostModifier": "address1",
        "StreetNamePostType": "address1",
        "CornerOf": "address1",
        "IntersectionSeparator": "address1",
        "LandmarkName": "address1",
        "USPSBoxGroupID": "address1",
        "USPSBoxGroupType": "address1",
        "USPSBoxID": "address1",
        "USPSBoxType": "address1",
        "OccupancyType": "address2",
        "OccupancyIdentifier": "address2",
        "SubaddressIdentifier": "address2",
        "SubaddressType": "address2",
        "PlaceName": "city",
        "StateName": "state",
        "ZipCode": "postal",
    }

    a = usaddress.tag(line, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
    if street_address == "None":
        street_address = "<MISSING>"
    city = a.get("city") or "<MISSING>"
    state = a.get("state") or "<MISSING>"
    postal = a.get("postal") or "<MISSING>"

    return street_address, city, state, postal


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def get_texts():
    data_url = "https://usainsuranceco.net/insurance-locations/"
    log.info(f"Crawling Locations Page: {data_url}")
    driver.get(data_url)
    time.sleep(30)
    tree = html.fromstring(driver.page_source, "lxml")
    driver.quit()
    return tree.xpath("//div[@class='entry-content']/p/iframe/@src")


def fetch_data():
    out = []
    page_url = "https://usainsuranceco.net/"
    log.info(f"Driver initiationed and now crawling {page_url}")
    driver.get(page_url)
    time.sleep(30)
    tree = html.fromstring(driver.page_source, "lxml")
    divs = tree.xpath("//div[@class='banner_box' and ./a]")
    texts = get_texts()
    log.info(f"Total Locations: {len(divs)}")
    for d in divs:
        text = texts.pop(0)
        line = (
            text.split("!2s")[1]
            .split("+USA")[0]
            .replace("+", " ")
            .replace("%2C", ",")
            .replace("%23", "#")
        )
        location_name = "".join(d.xpath("./h3/text()")).strip()
        street_address, city, state, postal = get_address(line)
        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            "".join(d.xpath(".//a[contains(@href, 'tel:')]/text()")).strip()
            or "<MISSING>"
        )
        latitude, longitude = get_coords_from_embed(text)
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"

        row = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            postal,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        out.append(row)

    return out


def scrape():
    log.info("Started Crawling")
    data = fetch_data()
    write_output(data)
    log.info("!!Finished Data Grabbing!!")


if __name__ == "__main__":
    scrape()
