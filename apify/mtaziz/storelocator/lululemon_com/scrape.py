from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl
from sgselenium import SgFirefox
from selenium.webdriver.common.action_chains import ActionChains

from lxml import html
import json
import time
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("lululemon_com")
DOMAIN_US = "lululemon.com"
DOMAIN_GLOBAL = "lululemon.co.uk"
URL_LOCATION_US_CA = "https://shop.lululemon.com/stores"
MISSING = SgRecord.MISSING


def get_special_headers():
    with SgFirefox(is_headless=True) as driver:
        requestName = "/cne/graphql"
        driver.get(URL_LOCATION_US_CA)
        driver.implicitly_wait(20)
        time.sleep(20)
        see_all_store_listings = '//a[contains(@href, "/stores/all-lululemon-stores")]'
        element1 = driver.find_element_by_xpath(see_all_store_listings).get_attribute(
            "href"
        )
        logger.info(f"Just to make sure all-lululemon-stores exists: {element1}")

        # Find out the lululemon all stores link so that we can load that page
        all_stores_find_element_by_xpath = driver.find_element_by_xpath(
            see_all_store_listings
        )

        # Hover your mouse to make the link workable
        hover = ActionChains(driver).move_to_element_with_offset(
            all_stores_find_element_by_xpath, 0, 0
        )
        hover.perform()

        # Click on it
        all_stores_find_element_by_xpath.click()
        driver.implicitly_wait(20)
        time.sleep(10)
        logger.info("The page is loaded")
        for r in driver.requests:
            logger.info(f"Finding /cne/graphql in {r.path}")
            if requestName in r.path:
                logger.info(f"Response Path GraphQL Found in {r.path}")
                return r.headers


def clean_raw_address(raw_address_):
    t5 = raw_address_.replace("None", "").replace(SgRecord.MISSING, "")
    t6 = t5.split(",")
    t7 = [i.strip().replace(".", "") for i in t6 if i]
    t8 = [i for i in t7 if i]
    t9 = ", ".join(t8)
    return t9


def fetch_us_ca_data():
    # This part scrape the data for the US and CA
    session_us_ca = SgRequests()
    headers_us_ca = {
        "accept": "application/json, text/plain, */*",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    }

    PAYLOAD = {
        "query": "{\n  storeLocatorList {\n    city\n    country\n    id\n    name\n    slug\n    state\n    stateDisplayName\n  }\n}\n"
    }
    headers_from_graphql_path = get_special_headers()
    API_ENDPOINT_URL_US_CA = "https://shop.lululemon.com/cne/graphql"
    response_sgr = session_us_ca.post(
        API_ENDPOINT_URL_US_CA,
        data=json.dumps(PAYLOAD),
        headers=dict(headers_from_graphql_path),
    )
    data_json_us_ca = json.loads(response_sgr.text)
    data_json_us_ca = data_json_us_ca["data"]["storeLocatorList"]
    for idx1, i in enumerate(data_json_us_ca[0:]):
        slug = i["slug"]
        page_url = f"https://shop.lululemon.com{slug}"
        logger.info(f"Pulling data from {idx1}: {page_url}")
        locator_domain = DOMAIN_US
        r_per_store = session_us_ca.get(page_url, headers=headers_us_ca, timeout=300)
        data_per_store = html.fromstring(r_per_store.text, "lxml")
        xpath_get_json_data = '//script[contains(@id, "__NEXT_DATA__")]/text()'
        data_json2 = data_per_store.xpath(xpath_get_json_data)
        data_json2 = json.loads("".join(data_json2))
        try:
            item = data_json2["props"]["pageProps"]["storeData"]

            # Location Name
            location_name = item["name"]
            logger.info(f"Location Name: {location_name}")

            # Address Data
            addinfo = item["fullAddress"]
            pa = parse_address_intl(addinfo)
            street_address = ""
            street_address_1 = pa.street_address_1
            street_address_2 = pa.street_address_2

            if street_address_2 is not None:
                street_address = street_address_1 + ", " + street_address_2
            else:
                if street_address_1 is not None:
                    street_address = street_address_1
                else:
                    street_address = MISSING

            city = item["city"]
            state = item["state"]

            # Zip code
            zip_postal = pa.postcode
            zip_postal = zip_postal if zip_postal else zip_postal

            # Country Code
            country_code = item["country"]
            country_code = country_code if country_code else country_code

            store_number = item["storeNumber"]
            logger.info(f"Store Number: {store_number}")

            latitude = item["latitude"] or MISSING
            longitude = item["longitude"] or MISSING
            location_type = item["storeType"] or MISSING

            # Phone
            try:
                phone = item["phone"]
            except:
                phone = MISSING
            if country_code == "US" or country_code == "CA":
                try:
                    if len(phone) < 5:
                        phone = MISSING
                except:
                    phone = MISSING

            # Hours of operation
            hours = ""
            for day in item["hours"]:
                try:
                    hrs = day["name"] + ": " + day["openHour"] + "-" + day["closeHour"]
                except:
                    hours = day["name"] + ": Closed"
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs

            hours_of_operation = hours if hours else MISSING
            raw_address = item["fullAddress"]
            raw_address = raw_address if raw_address else MISSING

            if store_number == "12019" and street_address == "23":
                street_address = street_address.replace("23", "23 E Main")

            if store_number == "11927" and street_address == "114":
                street_address = street_address.replace("114", "114 West County Center")

            if "300 Bob Wallace Ave" in street_address and store_number == "10752":
                street_address = "920 Bob Wallace Ave, Building 300, Unit 313"

            yield SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )
        except KeyError:
            continue


def fetch_global_data():
    # This is used to get the data from countries those are outside of US and CA
    session_global = SgRequests()
    headers_global = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    API_ENDPOINT_URL_GLOBAL = "https://www.lululemon.co.uk/on/demandware.store/Sites-UK-Site/en_GB/Stores-FindStores?showMap=true&radius=20000&lat=51.5073509&long=-0.1277583&lat=51.5073509&long=-0.1277583"
    json_data = session_global.get(
        API_ENDPOINT_URL_GLOBAL, headers=headers_global, timeout=300
    ).json()
    json_data_stores = json_data["stores"]
    data_locations_html = json_data["locations"]
    json_data_locations_html = json.loads(data_locations_html)
    for idx1, item in enumerate(json_data_stores):
        info_window_html = json_data_locations_html[idx1]["infoWindowHtml"]
        sel = html.fromstring(info_window_html, "lxml")
        page_url = sel.xpath(
            '//a[@class="btn btn-primary btn-block store-more-details"]/@href'
        )
        page_url = "".join(page_url)
        page_url = page_url if page_url else MISSING
        logger.info(f"Pulling data from {idx1}: {page_url}")
        locator_domain = DOMAIN_GLOBAL
        location_name = item["name"]
        logger.info(f"Location Name: {location_name}")
        street_address = ""
        street_address_raw_1 = item["address1"]
        street_address_raw_2 = item["address2"]

        if item["address2"] is not None:
            street_address = item["address1"] + ", " + item["address2"]
        else:
            if item["address1"] is not None:
                street_address = item["address1"]
            else:
                street_address = MISSING
        if street_address == "," or street_address == ".":
            street_address = MISSING

        street_address_raw_2 = item["address2"]

        city_raw = item["city"]
        city = city_raw if city_raw else MISSING
        if city == "," or city == ".":
            city = MISSING

        try:
            state_raw = item["stateCode"]
            state = state_raw if state_raw else MISSING
        except KeyError:
            state = MISSING
        if state == "," or state == ".":
            state = MISSING

        # Zip code
        zip_postal_raw = item["postalCode"]
        zip_postal = zip_postal_raw if zip_postal_raw else MISSING

        if zip_postal == "," or zip_postal == "." or zip_postal == "..":
            zip_postal = MISSING

        # Country Code
        country_code_raw = item["countryCode"]
        country_code = country_code_raw if country_code_raw else MISSING
        if str(country_code_raw) == "US" or str(country_code_raw) == "CA":
            continue

        store_number = item["ID"]
        logger.info(f"Store Number: {store_number}")

        latitude = item["latitude"] or MISSING
        longitude = item["longitude"] or MISSING
        location_type = MISSING
        if MISSING in str(latitude) and MISSING in str(longitude):
            continue

        # Phone
        try:
            phone = item["phone"]
        except:
            phone = MISSING
        if country_code == "US" or country_code == "CA":
            try:
                if len(phone) < 5:
                    phone = MISSING
            except:
                phone = MISSING

        # Hours of operation
        hours = sel.xpath('//div[@class="store-hours"]')
        hour_raw = ""
        for hour in hours:
            hour_raw = hour.xpath(".//div/text()")
            hour_raw = [" ".join(i.split()) for i in hour_raw]
        hour_raw = "; ".join(hour_raw)
        hours_of_operation = hour_raw if hour_raw else MISSING
        raw_address = f"{street_address_raw_1}, {street_address_raw_2}, {city}, {state}, {zip_postal_raw}, {country_code_raw}"
        clean_raw_address1 = clean_raw_address(raw_address)
        raw_address = clean_raw_address1 if clean_raw_address1 else MISSING

        if store_number == "12019" and street_address == "23":
            street_address = street_address.replace("23", "23 E Main")

        if store_number == "11927" and street_address == "114":
            street_address = street_address.replace("114", "114 West County Center")

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results_us_ca_data = list(fetch_us_ca_data())
        results_global_data = list(fetch_global_data())
        results_us_ca_data.extend(results_global_data)
        for rec in results_us_ca_data:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
