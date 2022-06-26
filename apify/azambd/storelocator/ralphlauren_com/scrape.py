from lxml import html
import time
import json
import random

from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from sgselenium.sgselenium import SgFirefox
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

DOMAIN = "ralphlauren.com"
website = "https://www.ralphlauren.com"
MISSING = "<MISSING>"

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def driverSleep(driver, time=2):
    try:
        WebDriverWait(driver, time).until(
            EC.presence_of_element_located((By.ID, MISSING))
        )
    except Exception as e1:
        log.info(f"Driver Err: {e1}")
        pass


def randomSleep(driver, start=5, limit=6):
    driverSleep(driver, random.randint(start, start + limit))


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
    if value is None or value == "None" or value == "":
        return MISSING
    return value


def fetch_stores():

    with SgFirefox(is_headless=True, block_third_parties=True) as driver:
        driver.get(f"{website}/stores")
        time.sleep(15)
        body = html.fromstring(driver.page_source, "lxml")
        allCountryCodes = body.xpath(
            "//select[@id='dwfrm_storelocator_country']/option/@value"
        )
        log.debug(f"Total country count: {len(allCountryCodes)} ...")
        allStores = []
        for countryCode in allCountryCodes[1:]:
            log.info(f"Now Fetching country {countryCode}")
            if countryCode == "BG":
                continue
            driver.get(
                f"{website}/findstores?dwfrm_storelocator_country={countryCode}&dwfrm_storelocator_findbycountry=Search&findByValue=CountrySearch"
            )
            randomSleep(driver, 20)
            body = html.fromstring(driver.page_source, "lxml")

            stores = json.loads(
                body.xpath('//div[contains(@class, "storeJSON hide")]/@data-storejson')[
                    0
                ]
            )
            jsonData = body.xpath(
                '//script[contains(@type, "application/ld+json")]/text()'
            )

            for data in jsonData:
                if 'store":[{' in data:
                    dataJSON = json.loads(data)["store"]
                    log.info(f"total stores in {countryCode} are {len(stores)}")
                    for store in stores:
                        store["location_name"] = MISSING
                        store["street_address"] = MISSING
                        store["hoo"] = MISSING
                        store["country_code"] = "US"
                        if "latitude" not in store:
                            continue

                        for data in dataJSON:
                            if (
                                "latitude" in data["geo"]
                                and f'{data["geo"]["latitude"]} {data["geo"]["longitude"]}'
                                == f'{store["latitude"]} {store["longitude"]}'
                            ):
                                store["location_name"] = data["name"]
                                store["street_address"] = data["address"][
                                    "streetAddress"
                                ]
                                store["country_code"] = data["address"][
                                    "addressCountry"
                                ]

                                ooh = []
                                if (
                                    data["openingHours"] == "LOCATION CLOSED"
                                    or data["openingHours"] == "Coming Soon"
                                    or data["openingHours"] == ""
                                    or data["openingHours"]
                                    == "By appointment only. | Solo su appuntamento."
                                ):
                                    store[
                                        "hoo"
                                    ] = "Monday: Closed, Tuesday: Closed, Wednesday: Closed, Thursday: Closed, Friday: Closed, Saturday: Closed, Sunday: Closed"
                                elif "By appointment only" in data["openingHours"]:
                                    store["hoo"] = MISSING
                                elif "appuntamento" in data["openingHours"]:
                                    store["hoo"] = MISSING
                                elif "temporarily closed" in data["openingHours"]:
                                    store["hoo"] = "temporarily closed"
                                elif "Opening mid-June" in data["openingHours"]:
                                    store["hoo"] = "Opening mid-June"
                                elif "Opening mid-May" in data["openingHours"]:
                                    store["hoo"] = "Opening mid-May"
                                elif "MON" in data["openingHours"]:
                                    store["hoo"] = (
                                        data["openingHours"]
                                        .replace("<br>\n", ", ")
                                        .replace("<br/>\n", ", ")
                                        .replace("<br/>", "")
                                    )
                                else:

                                    weeks_dict = json.loads(data["openingHours"])

                                    for day in [
                                        "monday",
                                        "tuesday",
                                        "wednesday",
                                        "thursday",
                                        "friday",
                                        "saturday",
                                        "sunday",
                                    ]:
                                        if "isClosed" in weeks_dict[day]:
                                            ooh.append(day.title() + ": Closed")
                                        else:
                                            ooh.append(
                                                day.title()
                                                + ": "
                                                + weeks_dict[day]["openIntervals"][0][
                                                    "start"
                                                ]
                                                + "-"
                                                + weeks_dict[day]["openIntervals"][0][
                                                    "end"
                                                ]
                                            )

                                    store["hoo"] = ", ".join(ooh)

            allStores = allStores + stores
        return allStores


def fetch_data():
    stores = fetch_stores()
    log.info(f"Total stores = {len(stores)}")
    for store in stores:

        location_type = MISSING

        store_number = getJSONObjectVariable(store, "id")
        page_url = f"{website}/Stores-Details?StoreID={store_number}"
        location_name = getJSONObjectVariable(store, "location_name")
        location_name = location_name.split("-")[0].strip()
        if location_name == MISSING:
            continue
        street_address = getJSONObjectVariable(store, "street_address")
        city = getJSONObjectVariable(store, "city")
        state = getJSONObjectVariable(store, "stateCode")
        zip_postal = getJSONObjectVariable(store, "postalCode")
        street_address = street_address.replace(f",{zip_postal}", "")

        if "temporarily closed" in str(street_address):
            location_type = "temporarily closed"

        country_code = getJSONObjectVariable(store, "country_code")
        phone = getJSONObjectVariable(store, "phone")
        latitude = getJSONObjectVariable(store, "latitude")
        longitude = getJSONObjectVariable(store, "longitude")

        hours_of_operation = getJSONObjectVariable(store, "hoo")
        hours_of_operation = (
            hours_of_operation.replace("<br/>\n", " ")
            .replace("<br/>", " ")
            .replace("<br>", " ")
            .replace("\n", " ")
            .replace("<br/", " ")
            .strip()
        )
        if "temporarily closed" in str(hours_of_operation):
            location_type = "temporarily closed"
        if "temporarily closed" in str(hours_of_operation):
            hours_of_operation = MISSING

        raw_address = f"{street_address}, {city}, {state} {zip_postal}".replace(
            MISSING, ""
        )
        raw_address = " ".join(raw_address.split())
        raw_address = raw_address.replace(", ,", ",").replace(",,", ",")
        if raw_address[len(raw_address) - 1] == ",":
            raw_address = raw_address[:-1]

        street_address = street_address.replace("Store temporarily closed. ,", "")
        street_address = street_address.replace(
            "Store re-opening 26th September. ,", ""
        )
        yield SgRecord(
            locator_domain=DOMAIN,
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
    log.info(f"Start scrapping {website} ...")
    start = time.time()
    count = 0

    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
            count = count + 1
    end = time.time()
    log.info(f"Total Rows Added= {count}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
