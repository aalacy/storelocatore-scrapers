from xml.etree import ElementTree as ET
import time
import json
import csv
from urllib.parse import urlparse
from lxml import html
import ssl

from sgselenium import SgChrome
from sgrequests import SgRequests
from sglogging import sglog

ssl._create_default_https_context = ssl._create_unverified_context


DOMAIN = "daynurseries.co.uk"

website = "https://www.daynurseries.co.uk"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
}
MISSING = "<MISSING>"
CSV_FILENAME = "data.csv"
COLUMNS = [
    "page_url",
    "location_name",
    "street_address",
    "city",
    "state",
    "zip_postal",
    "country_code",
    "store_number",
    "phone",
    "location_type",
    "latitude",
    "longitude",
    "locator_domain",
    "hours_of_operation",
    "brand_website",
]


session = SgRequests().requests_retry_session()
log = sglog.SgLogSetup().get_logger(logger_name=website)
driver = SgChrome(is_headless=True).driver()


def fetchStores():
    stores = []
    response = session.get(website + "/sitemaps/profile.xml", headers=headers)
    root = ET.fromstring(response.text)
    for elem in root:
        for var in elem:
            if "loc" in var.tag:
                stores.append(var.text)
    return stores


def fetchSinglePage(data_url, findRedirect=False):
    session = SgRequests()
    driver.get(data_url)
    incap_str = "/_Incapsula_Resource?SWJIYLWA=719d34d31c8e3a6e6fffd425f7e032f3"
    incap_url = website + incap_str
    session.get(incap_url)

    for request in driver.requests:
        headers = request.headers
        try:
            response = session.get(data_url, headers=headers)
            response_text = response.text

            test_html = response_text.split("div")

            if findRedirect and response_text.find("window.location.replace") > -1:
                try:
                    return response_text.split("window.location.replace('")[1].split(
                        "')"
                    )[0]
                except Exception:
                    continue
            elif len(test_html) < 2:
                continue
            else:
                return {
                    "response": response_text,
                    "hours_of_operation": getHoursOfOperation(),
                    "phone": getPhone(),
                }

        except Exception:
            continue


def getHoursOfOperation():
    try:
        hours_of_operation = []
        profileRows = driver.find_elements_by_xpath(
            "//div[contains(@class, 'profile-rows')]/div/ul"
        )

        for profileRow in profileRows:
            texts = []
            for li in profileRow.find_elements_by_xpath(".//li"):
                texts.append(li.text)
            if len(texts) > 1 and texts[0] == "Opening Days":
                hours_of_operation.append(f"Opening Days: {texts[1].strip()}")
            if len(texts) > 1 and texts[0] == "Opening Hours":
                hours_of_operation.append(f"Opening Hours: {texts[1].strip()}")
            if len(texts) > 1 and texts[0] == "When Closed":
                hours_of_operation.append(f"Closed: {texts[1].strip()}")
        hours_of_operation = "; ".join(hours_of_operation)
        return hours_of_operation
    except Exception as e:
        log.error("error loading hours_of_operation", e)
    return MISSING


def getPhone():
    try:
        driver.find_element_by_xpath("//a[@id='brochure_phone']").click()
        time.sleep(4)
        phones = driver.find_elements_by_xpath(
            "//div[@id='contacts_telephone_general']/p/strong/a"
        )
        for phone in phones:
            return phone.get_attribute("innerHTML")
    except Exception as e:
        log.error("error loading phone", e)
    return MISSING


def getScriptWithGeo(body):
    scripts = body.xpath("//script/text()")
    for script in scripts:
        if '"geo":{' in script:
            return json.loads(script)
    return None


def getVarName(value):
    try:
        return int(value)
    except ValueError:
        pass
    return value


def getJSONObjectVariable(Object, varNames, noVal=MISSING):
    value = noVal
    for varName in varNames.split("."):
        varName = getVarName(varName)
        try:
            value = Object[varName]
            Object = Object[varName]
        except Exception:
            return noVal
    return value


def fetchSingleStore(page_url):
    split_url = page_url.split("/")
    if len(split_url) != 6:
        log.error(f"Ignored {page_url} ...")
        return None
    log.info(f"Scrapping {page_url} ...")
    store_number = split_url[5]
    store_response = fetchSinglePage(page_url)

    hours_of_operation = getJSONObjectVariable(store_response, "hours_of_operation")
    phone = getJSONObjectVariable(store_response, "phone").strip()
    body = html.fromstring(store_response["response"], "lxml")

    geoJSON = getScriptWithGeo(body)
    location_name = getJSONObjectVariable(geoJSON, "name").strip().split(" at ")[0]

    address = {}
    if "address" in geoJSON:
        address = geoJSON["address"]

    street_address = getJSONObjectVariable(address, "streetAddress").strip()
    city = getJSONObjectVariable(address, "addressLocality").strip()
    state = getJSONObjectVariable(address, "addressRegion").strip()
    zip_postal = getJSONObjectVariable(address, "postalCode").strip()

    latitude = str(getJSONObjectVariable(geoJSON, "geo.latitude"))
    longitude = str(getJSONObjectVariable(geoJSON, "geo.longitude"))

    redirect_urls = body.xpath('//a[contains(@class, "button-website")]/@href')
    if len(redirect_urls) > 0:
        brand_website = fetchSinglePage(redirect_urls[0], True)
        brand_website = (urlparse(brand_website).netloc).replace("www.", "")

    else:
        brand_website = MISSING

    return {
        "page_url": page_url,
        "store_number": store_number,
        "location_name": location_name,
        "locator_domain": DOMAIN,
        "street_address": street_address,
        "city": city,
        "state": state,
        "zip_postal": zip_postal,
        "latitude": latitude,
        "longitude": longitude,
        "hours_of_operation": hours_of_operation,
        "brand_website": brand_website,
        "phone": phone,
        "country_code": "UK",
        "location_type": MISSING,
    }


def fetchData():
    stores = fetchStores()
    log.info(f"Total stores = {len(stores)}")

    file = open(CSV_FILENAME, "w")
    writer = csv.writer(file)
    writer.writerow(COLUMNS)

    for page_url in stores:
        try:
            data = fetchSingleStore(page_url)
        except Exception as e:
            log.error(f"Error fetching data {page_url}", e)
        if data is None:
            continue

        row = []
        for column in COLUMNS:
            if column in data and data[column] != "":
                row.append(data[column])
            else:
                row.append(MISSING)
        writer.writerow(row)

    file.close()
    driver.quit()


def scrape():
    start = time.time()
    fetchData()
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
