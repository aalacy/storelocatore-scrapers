from xml.etree import ElementTree as ET
import time
import json
from lxml import html
import ssl
from bs4 import BeautifulSoup as bs
from webdriver_manager.chrome import ChromeDriverManager
from sgselenium import SgChrome
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

ssl._create_default_https_context = ssl._create_unverified_context


DOMAIN = "daynurseries.co.uk"

website = "https://www.daynurseries.co.uk"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
}
MISSING = SgRecord.MISSING


session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetch_stores(driver):
    stores = []
    response = session.get(website + "/sitemaps/profile.xml", headers=headers)
    root = ET.fromstring(response.text)
    for elem in root:
        for var in elem:
            if "loc" in var.tag:
                stores.append(var.text)
    return stores


def fetch_single_page(driver, data_url, findRedirect=False):
    session = SgRequests()
    driver.get(data_url)
    incap_str = "/_Incapsula_Resource?SWJIYLWA=719d34d31c8e3a6e6fffd425f7e032f3"
    incap_url = website + incap_str
    session.get(incap_url)

    x = 0
    while True:
        x = x + 1
        if x == 10:
            break
        for request in driver.requests:
            headers = dict(request.headers)
            try:
                response = session.get(data_url, headers=headers)
                response_text = response.text

                test_html = response_text.split("div")

                if findRedirect and response_text.find("window.location.replace") > -1:

                    try:
                        return [
                            session,
                            headers,
                            response_text.split("window.location.replace('")[1].split(
                                "')"
                            )[0],
                        ]
                    except Exception:
                        continue
                elif len(test_html) < 2:
                    continue
                else:

                    return [
                        session,
                        headers,
                        {
                            "response": response_text,
                            "hours_of_operation": get_hours_of_operation(response_text),
                            "phone": get_phone(session, headers, response_text),
                        },
                    ]

            except Exception:
                continue


def get_hours_of_operation(response_text):
    try:
        hours_of_operation = []

        hoosoup = html.fromstring(response_text, "lxml")
        profileRows = hoosoup.xpath(
            "//div[contains(@class, 'profile-row-section')]/div/ul"
        )

        for profileRow in profileRows:
            texts = []
            for li in profileRow.xpath(".//li | .//li/div"):
                texts.append(li.text)
            if len(texts) > 1 and texts[1] == "Opening Days":
                hours_of_operation.append(f"Opening Days: {texts[2].strip()}")
            if len(texts) > 1 and texts[1] == "Opening Hours":
                hours_of_operation.append(f"Opening Hours: {texts[2].strip()}")
            if len(texts) > 1 and texts[1] == "When Closed":
                hours_of_operation.append(f"Closed: {texts[2].strip()}")
        hours_of_operation = "; ".join(hours_of_operation)
        return hours_of_operation
    except Exception as e:
        log.error("error loading hours_of_operation", e)
    return MISSING


def get_phone(session, headers, response_text):
    try:
        phone_soup = bs(response_text, "html.parser")
        phone_soup = html.fromstring(response_text, "lxml")
        phone_link = phone_soup.xpath('//button[@id="brochure_phone"]/@href')
        if len(phone_link) == 0:
            return MISSING
        phone_link = phone_link[0]

        phone_response = session.get(phone_link, headers=headers).text
        response_soup = bs(phone_response, "html.parser")
        phone = (
            response_soup.find("div", attrs={"class": "contacts_telephone"})
            .find("a")
            .text.strip()
        )
        return phone
    except Exception as e:
        log.error("error loading phone", e)
        return "broken"


def get_scriptWith_geo(body):
    scripts = body.xpath("//script/text()")
    for script in scripts:
        if '"geo":{' in script:
            return json.loads(script)
    return None


def get_var_name(value):
    try:
        return int(value)
    except ValueError:
        pass
    return value


def get_JSON_object_variable(Object, varNames, noVal=MISSING):
    value = noVal
    for varName in varNames.split("."):
        varName = get_var_name(varName)
        try:
            value = Object[varName]
            Object = Object[varName]
        except Exception:
            return noVal
    return value


def fetch_single_store(driver, page_url, session=None, headers=None):

    split_url = page_url.split("/")
    if len(split_url) != 6:
        log.error(f"Ignored {page_url} ...")
        return None
    log.info(f"Scrapping {page_url} ...")
    store_number = split_url[5]

    if session is None:
        store_response_session = fetch_single_page(driver, page_url)
        session = store_response_session[0]
        headers = store_response_session[1]
        store_response = store_response_session[2]

    else:
        response_text = session.get(page_url, headers=headers).text
        test_html = test_html = response_text.split("div")

        if len(test_html) < 2:
            store_response_session = fetch_single_page(driver, page_url)
            session = store_response_session[0]
            headers = store_response_session[1]
            store_response = store_response_session[2]

        else:
            store_response = {
                "response": response_text,
                "hours_of_operation": get_hours_of_operation(response_text),
                "phone": get_phone(session, headers, response_text),
            }

    hours_of_operation = get_JSON_object_variable(store_response, "hours_of_operation")
    phone = get_JSON_object_variable(store_response, "phone").strip()
    body = html.fromstring(store_response["response"], "lxml")

    geoJSON = get_scriptWith_geo(body)
    location_name = get_JSON_object_variable(geoJSON, "name").strip().split(" at ")[0]

    address = {}
    if "address" in geoJSON:
        address = geoJSON["address"]

    street_address = get_JSON_object_variable(address, "streetAddress").strip()
    city = get_JSON_object_variable(address, "addressLocality").strip()
    state = get_JSON_object_variable(address, "addressRegion").strip()
    zip_postal = get_JSON_object_variable(address, "postalCode").strip()

    latitude = str(get_JSON_object_variable(geoJSON, "geo.latitude"))
    longitude = str(get_JSON_object_variable(geoJSON, "geo.longitude"))

    return [
        session,
        headers,
        {
            "location_type": MISSING,
            "raw_address": MISSING,
            "page_url": page_url,
            "store_number": store_number,
            "location_name": location_name,
            "street_address": street_address,
            "city": city,
            "state": state,
            "zip_postal": zip_postal,
            "latitude": latitude,
            "longitude": longitude,
            "hours_of_operation": hours_of_operation,
            "phone": phone,
            "country_code": "UK",
        },
    ]


def fetch_data(driver, writer):
    stores = fetch_stores(driver)
    log.info(f"Total stores = {len(stores)}")

    x = 0
    data = "x"
    for page_url in stores[0:]:
        x = x + 1
        if x == 1:
            continue

        if x == 2:
            try:
                data_session_headers = fetch_single_store(driver, page_url)
                data = data_session_headers[2]
                session = data_session_headers[0]
                headers = data_session_headers[1]
            except Exception as e:
                log.error(f"Error fetching data {page_url}", e)
            if data == "x":
                continue

        else:
            try:
                data_session_headers = fetch_single_store(
                    driver, page_url, session, headers
                )
                data = data_session_headers[2]
                session = data_session_headers[0]
                headers = data_session_headers[1]
            except Exception as e:
                log.error(f"Error fetching data {page_url}", e)
            if data is None:
                continue

        rec = SgRecord(
            locator_domain=DOMAIN,
            store_number=data["store_number"],
            page_url=data["page_url"],
            location_name=data["location_name"],
            location_type=data["location_type"],
            street_address=data["street_address"],
            city=data["city"],
            zip_postal=data["zip_postal"],
            state=data["state"],
            country_code=data["country_code"],
            phone=data["phone"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            hours_of_operation=data["hours_of_operation"],
            raw_address=data["raw_address"],
        )
        writer.write_row(rec)


def scrape():
    start = time.time()
    with SgChrome(executable_path=ChromeDriverManager().install()).driver() as driver:
        with SgWriter(
            deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)
        ) as writer:
            fetch_data(driver, writer)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
