from lxml import html
import time
import json

from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgrequests import SgRequests

from sgselenium.sgselenium import SgFirefox
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

DOMAIN = "ralphlauren.com"
website = "https://www.ralphlauren.com"
website2 = "https://www.ralphlauren.global"
MISSING = SgRecord.MISSING

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

http = SgRequests()

headers = {
    "authority": "www.ralphlauren.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9",
    "Cookie": "_pxhd=X6pf-dLqFYkjA1LCKGtlPcl6cBFRCPs2iYVwqyoWVpmiFne2kEErCndacgOYkLxn29-FWBi6qwzPKYEWlZwMxw==:12sFThbmi9og/ljBydM0KoHlehInIUBYxzxYO6/WGs7n2lITdGW7TYErdUnag15C7RF6ZBTBgKthZz3cwHYRWl8QaT7avj6thDZEdTbEvcA=",
}


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
    if value is None or value == "None" or value == "":
        return MISSING
    return value


def fetch_stores():
    response = http.get(f"{website2}/Stores-ShowCountries", headers=headers)

    body = html.fromstring(response.text, "lxml")
    countries = body.xpath('//a[contains(@class, "store-directory-countrylink")]/@href')
    log.info(f"Total countries ={len(countries)}")

    countryCount = 0

    stores = []
    for country in countries:

        countryCount = countryCount + 1
        log.info(f"{countryCount}. scrapping country {country}")
        if (
            "AZ" in str(country)
            or "BH" in str(country)
            or "BR" in str(country)
            or "HU" in str(country)
            or "IL" in str(country)
            or "MA" in str(country)
            or "QA" in str(country)
            or "SA" in str(country)
            or "AE" in str(country)
        ):
            log.info(f"Target: {website}{country}")
            response = http.get(f"{website}{country}", headers=headers)
            body = html.fromstring(response.text, "lxml")
            cities = body.xpath(
                '//a[contains(@class, "store-directory-citylink")]/@href'
            )
            log.info(f"{countryCount}. total city = {len(cities)}")

            cityCount = 0
            for city in cities:
                cityCount = cityCount + 1
                pages = body.xpath(
                    '//a[contains(@class, "store-directory-citylink")]/@href'
                )
                log.info(f"{countryCount}==> {cityCount}. scrapping city {len(pages)}")
                for page in pages:
                    with SgFirefox(driver_wait_timeout=100) as driver:
                        driver.get(f"{website}{page}")
                        body = html.fromstring(driver.page_source, "lxml")
                        dataSet = body.xpath(
                            '//div[contains(@class,"storeJSON")]/@data-storejson'
                        )
                        for data in dataSet:
                            stores = stores + json.loads(data)
    return stores


def fetch_data():
    stores = fetch_stores()
    log.info(f"Total stores = {len(stores)}")
    for store in stores:

        location_type = MISSING

        store_number = get_JSON_object_variable(store, "id")
        page_url = f"{website}/Stores-Details?StoreID={store_number}"
        location_name = get_JSON_object_variable(store, "location_name")
        location_name = location_name.split("-")[0].strip()
        street_address = get_JSON_object_variable(store, "street_address")
        city = get_JSON_object_variable(store, "city")
        state = get_JSON_object_variable(store, "stateCode")
        zip_postal = get_JSON_object_variable(store, "postalCode")
        country_code = get_JSON_object_variable(store, "countryCode")
        phone = get_JSON_object_variable(store, "phone")
        latitude = get_JSON_object_variable(store, "latitude")
        longitude = get_JSON_object_variable(store, "longitude")

        street_address = street_address.replace(f",{zip_postal}", "").replace(",", ", ")
        street_address = " ".join(street_address.split())

        hours_of_operation = get_JSON_object_variable(store, "hoo")

        if location_name == MISSING:
            log.info(f"Fetching page_url by SgFireFox: {page_url} ...")
            with SgFirefox(driver_wait_timeout=100) as driver:
                driver.get(page_url)
                body = html.fromstring(driver.page_source, "lxml")
                jsonData = body.xpath(
                    '//script[contains(@type, "application/ld+json")]/text()'
                )

                for data in jsonData:
                    if '"openingHours"' in data:
                        try:
                            dataJSON = json.loads(data)
                        except Exception as e:
                            log.error(f"Failed to load json openingHours: {e}")
                            dataJSON = []
                        location_name = dataJSON["name"]
                        hours_of_operation = (
                            "; ".join(dataJSON["openingHours"])
                            .replace("<br/>\n", "; ")
                            .replace("<br/>", " ")
                            .replace("<br>", "; ")
                            .replace("\n", " ")
                            .strip()
                        )
                jsonDataAddr = body.xpath(
                    '//script[contains(@type, "application/ld+json")]/text()'
                )[4]

                dataforaddr = json.loads(jsonDataAddr)
                street_address = dataforaddr["address"]["streetAddress"]
                street_address = street_address.replace("," + zip_postal, "")

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
        )
    return []


def scrape():
    log.info("Crawling started ...")
    start = time.time()

    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
