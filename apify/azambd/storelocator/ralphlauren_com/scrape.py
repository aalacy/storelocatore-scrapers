from lxml import html
import time
import json
import ast
import pycountry
from sgpostal.sgpostal import parse_address_intl

from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgrequests import SgRequests

import ssl

ssl._create_default_https_context = ssl._create_unverified_context


DOMAIN = "ralphlauren.com"
website = "https://www.ralphlauren.com"
MISSING = SgRecord.MISSING

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


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


def do_fuzzy_search(country):
    try:
        result = pycountry.countries.search_fuzzy(country)
    except Exception:
        return None
    else:
        return result[0].alpha_2


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


def get_address(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_intl(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode

            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            return street_address, city, state
    except Exception as e:
        log.info(f"No Address {e}")
        pass
    return MISSING, MISSING, MISSING


def fetch_stores(http):
    response = http.get(f"{website}/Stores-ShowCountries", headers=headers)

    body = html.fromstring(response.text, "lxml")
    countries = body.xpath('//a[contains(@class, "store-directory-countrylink")]/@href')
    log.debug(f"Total countries ={len(countries)}")

    countryCount = 0

    stores = []
    for country in countries:
        countryCount = countryCount + 1
        log.debug(f"{countryCount}. scrapping country {country}")
        response = http.get(f"{website}{country}", headers=headers)
        body = html.fromstring(response.text, "lxml")
        cities = body.xpath('//a[contains(@class, "store-directory-citylink")]/@href')
        log.debug(f"{countryCount}. total city = {len(cities)}")

        cityCount = 0
        for city in cities:
            cityCount = cityCount + 1
            pages = body.xpath(
                '//a[contains(@class, "store-directory-citylink")]/@href'
            )
            log.debug(f"{countryCount}==> {cityCount}. scrapping city {len(pages)}")
            for page in pages:
                response = http.get(f"{website}{page}", headers=headers)
                body = html.fromstring(response.text, "lxml")
                dataSet = body.xpath(
                    '//div[contains(@class,"storeJSON")]/@data-storejson'
                )
                for data in dataSet:
                    stores = stores + json.loads(data)
    return stores


def fetch_data(http):
    stores = fetch_stores(http)
    log.info(f"Total stores = {len(stores)}")
    for store in stores:

        location_type = MISSING

        store_number = get_JSON_object_variable(store, "id")
        page_url = f"{website}/Stores-Details?StoreID={store_number}"
        location_name = get_JSON_object_variable(store, "location_name")
        location_name = location_name.split("-")[0].strip()
        zip_postal = get_JSON_object_variable(store, "postalCode")
        country = get_JSON_object_variable(store, "countryCode")
        country_code = do_fuzzy_search(country)
        phone = get_JSON_object_variable(store, "phone")
        latitude = get_JSON_object_variable(store, "latitude")
        longitude = get_JSON_object_variable(store, "longitude")

        if location_name == MISSING:
            log.info(f"Fetching page_url {page_url} ...")
            time.sleep(5)
            response = http.get(f"{page_url}", headers=headers)
            body = html.fromstring(response.text, "lxml")
            try:
                jsonData = body.xpath(
                    '//script[contains(@type, "application/ld+json")]/text()'
                )[3].strip()
                data = ast.literal_eval(jsonData)
                location_name = data["name"]
                location_name = location_name.split("-")[0].strip()
                log.info(f"Location Name: {location_name}")
                street_address = data["address"]["streetAddress"]
                log.info(f"Street Address: {street_address}")
                address2 = data["address"]["addressLocality"]
                raw_address = f"{street_address}, {address2}"

                street_address, city, state = get_address(raw_address)

                hoo = []
                hoos = body.xpath('//tr[@class="store-hourrow"]')
                if len(hoos) > 1:
                    for h in hoos:
                        day = (
                            h.xpath('./td[@class="store-hours-day"]/text()')[0]
                            .strip()
                            .replace(">", "")
                        )
                        try:
                            hrs = h.xpath('./td[@class="store-hours-open"]/text()')[0]
                            hoo.append(f"{day}:{hrs}")
                        except:
                            hoo.append(f"{day}")
                            pass

                else:
                    for h in hoos:
                        day = (
                            "".join(h.xpath('./td[@class="store-hours-day"]/text()'))
                            .strip()
                            .replace("\n", ",")
                        )
                        hoo.append(f"{day}")

                hours_of_operation = ";".join(hoo)
            except Exception as e:
                log.debug(f"Failed loading page, {e}")

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
    log.info("Crawling started ...")
    start = time.time()
    with SgRequests() as http:
        with SgWriter(
            deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
        ) as writer:
            for rec in fetch_data(http):
                writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
