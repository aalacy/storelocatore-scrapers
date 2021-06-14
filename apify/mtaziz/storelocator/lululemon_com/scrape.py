from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgpostal import parse_address_intl
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
DOMAIN = "https://www.lululemon.com"
URL_LOCATION = "https://shop.lululemon.com/stores"
URL_LOCATION_ALL_STORES = "https://shop.lululemon.com/stores/all-lululemon-stores"

MISSING = "<MISSING>"

headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}

session = SgRequests()


def get_special_headers():
    with SgFirefox(is_headless=True) as driver:
        requestName = "/cne/graphql"
        driver.get(URL_LOCATION)
        driver.implicitly_wait(20)
        time.sleep(10)
        see_all_store_listings = '//a[contains(@href, "/stores/all-lululemon-stores")]'
        element1 = driver.find_element_by_xpath(see_all_store_listings).get_attribute(
            "href"
        )
        logger.info(f"Just to make sure all-lululemon-stores exists: {element1}")

        # Find out the lululemon all stores link so that we can load that page
        all_stores_find_element_by_class = driver.find_element_by_class_name(
            "ctaBlock-GVjCz"
        )

        # Hover your mouse to make the link workable
        hover = ActionChains(driver).move_to_element_with_offset(
            all_stores_find_element_by_class, 0, 0
        )
        hover.perform()

        # Click on it
        all_stores_find_element_by_class.click()
        driver.implicitly_wait(20)
        time.sleep(10)
        logger.info("The page is loaded")
        for r in driver.requests:
            logger.info(f"Finding /cne/graphql in {r.path}")
            if requestName in r.path:
                logger.info(f"Response Path GraphQL Found in {r.path}")
                return r.headers


def fetch_data():
    PAYLOAD = {
        "query": "{\n  storeLocatorList {\n    city\n    country\n    id\n    name\n    slug\n    state\n    stateDisplayName\n  }\n}\n"
    }
    headers_from_graphql_path = get_special_headers()
    API_ENDPOINT_URL = "https://shop.lululemon.com/cne/graphql"
    response_sgr = session.post(
        API_ENDPOINT_URL,
        data=json.dumps(PAYLOAD),
        headers=dict(headers_from_graphql_path),
    )
    data_json1 = json.loads(response_sgr.text)
    s = set()
    data_json1 = data_json1["data"]["storeLocatorList"]
    for idx1, i in enumerate(data_json1):
        slug = i["slug"]
        page_url = f"https://shop.lululemon.com{slug}"
        logger.info(f"Pulling data from {idx1}: {page_url}")
        locator_domain = DOMAIN
        r_per_store = session.get(page_url, headers=headers)
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
            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING
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
            if store_number in s:
                continue
            s.add(store_number)

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


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
