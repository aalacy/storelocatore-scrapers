from sgscrape.sgpostal import parse_address_intl
from lxml import html
import re
import time
import json

from sgrequests import SgRequests
from sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord

from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

website = "https://www.patagonia.com"
MISSING = "<MISSING>"
api_url = "https://patagonia.locally.com/stores/conversion_data?has_data=true&company_id=30&store_mode=&style=&color=&upc=&category=&inline=1&show_links_in_list=&parent_domain=&map_center_lat=40.78831928091212&map_center_lng=-74.06000000000097&map_distance_diag=3000&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=false&zoom_level=.json"

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
headers = {"user-agent": user_agent}


log = sglog.SgLogSetup().get_logger(logger_name=website)

days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def get_page(url):
    session = SgRequests()
    log.info(f"URL: {url}")
    return session.get(url, headers=headers)


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


def getAddress(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_intl(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            postcode = data.postcode
            if street_address is None or street_address == "":
                street_address = MISSING
            if city is None or city == "":
                city = MISSING
            if state is None or state == "":
                state = MISSING
            if postcode is None or postcode == "":
                postcode = MISSING
            return street_address, city, state, postcode
    except Exception as e:
        log.info(f"Address Err: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def getHooViaDriver(driver, page_url):
    driver.get(page_url)
    response = driver.page_source

    body = html.fromstring(response, "lxml")
    hoo = fetchLxmlText(
        body,
        '//strong[contains(text(), "Opening Hours")]/following-sibling::text()',
        "; ",
    )
    if hoo == MISSING:
        hoo = fetchLxmlText(
            body,
            '//strong[contains(text(), "Store Hours")]/following-sibling::text()',
            "; ",
        )
    if hoo == MISSING:
        hoo = fetchLxmlText(
            body, '//div[contains(@class, "store-details-hours--full")]/p/text()', "; "
        )
    return hoo


def fetchSinglePage(driver, page_url, country_code):
    response = get_page(page_url)
    body = html.fromstring(response.text, "lxml")
    latitude = fetchLxmlText(body, '//div[@class="store-locator-map"]/@data-latitude')
    longitude = fetchLxmlText(body, '//div[@class="store-locator-map"]/@data-longitude')
    hoo = fetchLxmlText(
        body,
        '//strong[contains(text(), "Opening Hours")]/following-sibling::text()',
        "; ",
    )
    if hoo == MISSING:
        hoo = fetchLxmlText(
            body,
            '//strong[contains(text(), "Store Hours")]/following-sibling::text()',
            "; ",
        )
    if hoo == MISSING:
        hoo = fetchLxmlText(
            body, '//div[contains(@class, "store-details-hours--full")]/p/text()', "; "
        )

    if hoo == MISSING:
        hoo = getHooViaDriver(driver, page_url)
    hoo = hoo.replace(": Monday", "Monday").replace(":; ", "").strip()
    return hoo, latitude, longitude


def fetchCountry(driver, country_code):
    stores = []
    country_url = f"{website}/store-locator/?dwfrm_wheretogetit_country={country_code}"
    response = get_page(country_url)
    body = html.fromstring(response.text, "lxml")
    pageStores = body.xpath('//div[@class="store-info"]')
    log.debug(f"Scrapping country={country_code}; stores = {len(pageStores)}")

    for pageStore in pageStores:
        location_type = "Patagonia Retail Stores"
        page_url = website + pageStore.xpath('.//div[@class="store-name"]/a/@href')[0]
        location_name = fetchLxmlText(pageStore, './/div[@class="store-name"]/a/text()')
        raw_address = (
            fetchLxmlText(pageStore, './/div[@class="store-addr"]/text()')
            + " "
            + fetchLxmlText(pageStore, './/div[@class="store-location"]/text()')
        )
        phone = fetchLxmlText(pageStore, './/a[contains(@href, "tel")]/text()').replace(
            "p:", ""
        )

        store_number = MISSING
        stn = page_url.split("store_")[1].split(".html")[0].strip()
        if stn.isdigit():
            store_number = stn

        if (
            "cid=store_206469445" in page_url
            or "cid=store_Patagonia-Tu-Cheng-Outlet" in page_url
        ):
            page_url = country_url

        street_address, city, state, zip_postal = getAddress(raw_address)
        hoo, latitude, longitude = fetchSinglePage(driver, page_url, country_code)

        stores.append(
            {
                "location_name": location_name,
                "page_url": page_url,
                "store_number": store_number,
                "phone": phone,
                "location_type": location_type,
                "country_code": country_code,
                "street_address": street_address,
                "city": city,
                "state": state,
                "zip_postal": zip_postal,
                "raw_address": raw_address,
                "latitude": latitude,
                "longitude": longitude,
                "hoo": hoo,
            }
        )

    return stores


def getHoo(data):
    hours_of_operation = []
    for day in days:
        d_open = getJSONObjectVariable(data, f"{day}_time_open", 0)
        d_close = getJSONObjectVariable(data, f"{day}_time_close", 0)
        if d_open != 0 and d_close != 0:
            o1, o2 = divmod(d_open, 100)
            c1, c2 = divmod(d_close, 100)
            if o2 < 10:
                o2 = f"{o2}0"
            if c2 < 10:
                c2 = f"{c2}0"
            hours_of_operation.append(f"{day.capitalize()}: {o1}:{o2}-{c1}:{c2}")
    if len(hours_of_operation) == 0:
        return MISSING
    hours_of_operation = "; ".join(hours_of_operation)
    return hours_of_operation


def convertJSData(data={}):
    street_address = getJSONObjectVariable(data, "address")
    city = getJSONObjectVariable(data, "city")
    state = getJSONObjectVariable(data, "state")
    zip_postal = getJSONObjectVariable(data, "zip")
    raw_address = f"{street_address} {city}, {state} {zip_postal}"

    return {
        "location_name": getJSONObjectVariable(data, "name"),
        "page_url": "https://www.patagonia.com/store-locator",
        "store_number": getJSONObjectVariable(data, "id"),
        "phone": getJSONObjectVariable(data, "phone"),
        "location_type": "Authorized Patagonia Dealer",
        "country_code": getJSONObjectVariable(data, "country"),
        "street_address": street_address,
        "city": city,
        "state": state,
        "zip_postal": zip_postal,
        "raw_address": raw_address,
        "latitude": getJSONObjectVariable(data, "lat"),
        "longitude": getJSONObjectVariable(data, "lng"),
        "hoo": getHoo(data),
    }


def fetchStores():
    stores = []
    session = SgRequests()
    response = session.get(api_url, headers=headers)
    log.info(response)
    jsData = json.loads(response.text)["markers"]
    log.info(f"Total stores from api = {len(jsData)}")
    for data in jsData:
        stores.append(convertJSData(data))
    response = get_page(f"{website}/store-locator")
    body = html.fromstring(response.text, "lxml")
    country_codes = body.xpath('//select[@class="input-select country"]/option/@value')
    log.info(f"Total country codes = {len(country_codes)}")

    driver = initiateDriver()
    for country_code in country_codes:
        if country_code == "JP":
            continue
        stores = stores + fetchCountry(driver, country_code)

    if driver is not None:
        driver.close()
    return stores


def fetchLxmlText(body, xpath, delimiter=" "):
    elements = body.xpath(xpath)
    value = ""
    for element in elements:
        element = (
            element.replace("\r", "").replace("\n", "").replace("&nbsp; ", "").strip()
        )
        element = re.sub(r"\s+", " ", element)
        if len(element):
            if len(value):
                value = value + delimiter + element
            else:
                value = element
    if len(value) == 0:
        return MISSING
    return value.strip()


def initiateDriver(driver=None):
    if driver is not None:
        driver.close()

    return SgChrome(
        is_headless=True,
        executable_path=ChromeDriverManager().install(),
        user_agent=user_agent,
    ).driver()


def fetchData():
    stores = fetchStores()
    log.info(f"Total stores = {len(stores)}")
    for store in stores:
        store_number = store["store_number"]
        page_url = store["page_url"]
        location_name = store["location_name"]
        location_type = store["location_type"]
        street_address = store["street_address"]
        city = store["city"]
        zip_postal = store["zip_postal"]
        state = store["state"]
        country_code = store["country_code"]
        phone = store["phone"]
        latitude = store["latitude"]
        longitude = store["longitude"]
        hours_of_operation = store["hoo"]
        raw_address = store["raw_address"]

        yield SgRecord(
            locator_domain=website,
            store_number=store_number,
            page_url=page_url,
            location_name=location_name,
            location_type=location_type,
            street_address=street_address,
            city=city,
            zip_postal=zip_postal,
            state=state,
            country_code=country_code,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )
    return []


def scrape():
    start = time.time()
    result = fetchData()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        for rec in result:
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
