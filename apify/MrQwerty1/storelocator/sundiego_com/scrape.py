import csv
import ssl
import time
import usaddress

from lxml import html
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

from sglogging import SgLogSetup

log = SgLogSetup().get_logger("sundiego.com")
user_agent = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Mobile Safari/537.36"

MISSING = "<MISSING>"


def initiateDriver(driver=None):
    if driver is not None:
        driver.quit()

    return SgChrome(
        is_headless=True,
        user_agent=user_agent,
        executable_path=ChromeDriverManager().install(),
    ).driver()


def driverSleep(driver, time=10):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except Exception:
        pass


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

    try:
        a = usaddress.tag(line, tag_mapping=tag)[0]
    except usaddress.RepeatedLabelError:
        street = line.split(",")[0].strip()
        city = line.split(",")[1].strip()
        postal = line.split(",")[-1].strip()
        a = {"address1": street, "city": city, "postal": postal}

    street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
    if street_address == "None":
        street_address = MISSING
    city = a.get("city") or MISSING
    state = a.get("state") or MISSING
    postal = a.get("postal") or MISSING

    return street_address, city, state, postal


def fetch_data():
    out = []
    locator_domain = "https://sundiego.com/"
    page_url = "https://sundiego.com/pages/sun-diego-store-locations"
    log.info("Initiating Chrome Driver")
    driver = initiateDriver()
    driver.get(page_url)
    driverSleep(driver)
    source = driver.page_source

    tree = html.fromstring(source)
    divs = tree.xpath("//table//tr")

    for d in divs:
        _tmp = []
        lines = d.xpath(".//text()")
        for line in lines:
            if not line.strip() or "Email" in line or "__" in line:
                continue
            _tmp.append(line.replace("Phone:", "").replace("\xa0", "").strip())

        location_name = _tmp.pop(0)
        line = ", ".join(_tmp[:2])
        _tmp = _tmp[2:]
        street_address, city, state, postal = get_address(line)
        if city == "Del":
            city += f" {state}"
            state = "<MISSING>"
        if city == "<MISSING>":
            city = state
            state = "<MISSING>"

        country_code = "US"
        store_number = "<MISSING>"
        phone = _tmp.pop(0)
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = ";".join(_tmp).replace(":;", ":") or "<MISSING>"

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
    driver.quit()
    return out


def scrape():
    log.info("Started")
    start = time.time()
    data = fetch_data()
    write_output(data)
    log.info(f"Finished Data Grabbing, added total rows {len(data)}")
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    ssl._create_default_https_context = ssl._create_unverified_context
    scrape()
