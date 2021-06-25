from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium import SgFirefox
from webdriver_manager.firefox import GeckoDriverManager
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from lxml import html
from time import sleep


import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("marriott_com__gaylord-hotels__travel_mi")
DOMAIN = "https://www.marriott.com/"
MISSING = "<MISSING>"
headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "upgrade-insecure-requests": "1",
}


def get_all_store_urls():
    all_store_urls = []
    start_url = "https://www.marriott.com/hotel-search.mi"
    with SgFirefox(
        executable_path=GeckoDriverManager().install(), is_headless=True
    ) as driver:

        driver.get(start_url)
        sleep(10)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//a[contains(text(), "View all hotels")]')
            )
        )
        us = driver.find_element_by_xpath('//a[contains(text(), "View all hotels")]')
        driver.execute_script("arguments[0].scrollIntoView();", us)
        us.click()
        sleep(10)
        logger.info("View All Hotels in the US")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//span[@data-target="brands"]'))
        )
        driver.find_element_by_xpath('//span[@data-target="brands"]').click()
        sleep(5)
        logger.info("brand filter gaylord applied")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a[@data-for="brands_GE"]'))
        )
        brand_ge = driver.find_element_by_xpath('//a[@data-for="brands_GE"]')
        driver.execute_script("arguments[0].click();", brand_ge)
        sleep(5)

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//button[@class="m-button m-button-primary l-float-right l-button-50 l-button cta-apply"]',
                )
            )
        )
        apply_button = driver.find_element_by_xpath(
            '//button[@class="m-button m-button-primary l-float-right l-button-50 l-button cta-apply"]'
        )
        driver.execute_script("arguments[0].scrollIntoView();", apply_button)
        driver.execute_script("arguments[0].click();", apply_button)
        sleep(5)
        logger.info(" Apply Button Clicked with Success")
        sleep(50)

        dom = html.fromstring(driver.page_source, "lxml")
        all_locations = dom.xpath('//a[@class="t-alt-link analytics-click"]/@href')
        logger.info(f"All Loctions: {all_locations}")
        all_store_urls.extend(all_locations)
    all_store_urls = [
        "https://www.marriott.com/hotels/travel/" + url.split("/")[-2] + "/"
        for url in all_store_urls
    ]
    return all_store_urls


def fetch_data():
    # Your scraper here

    session = SgRequests()

    all_locations = get_all_store_urls()
    logger.info(f"all locations URLs: {all_locations}")
    for url in all_locations:
        page_url = url
        logger.info(f"Pulling the data from: {page_url} ")
        loc_response = session.get(page_url, headers=headers)
        loc_dom = html.fromstring(loc_response.text, "lxml")
        poi = loc_dom.xpath('//script[@data-component-name="schemaOrg"]/text()')
        if poi:
            locator_domain = DOMAIN
            poi = json.loads(poi[0])
            poi = [e for e in poi["@graph"] if e["@type"] == "Hotel"][0]
            location_name = poi["name"]
            location_name = location_name if location_name else MISSING
            street_address = poi["address"]["streetAddress"] or MISSING
            city = poi["address"]["addressLocality"] or MISSING
            state = poi["address"]["addressRegion"] or MISSING
            if state == "Tennessee":
                state = "TN"
            zip_postal = poi["address"]["postalCode"] or MISSING
            country_code = poi["address"]["addressCountry"]
            if country_code == "USA":
                country_code = "US"
            country_code = country_code if country_code else MISSING
            store_number = MISSING
            phone = poi["telephone"] or MISSING
            phone = phone if phone else MISSING
            location_type = "Gaylord Hotels - Marriott"
            latitude = poi["geo"]["latitude"] or MISSING
            longitude = poi["geo"]["longitude"] or MISSING
            hours_of_operation = MISSING
            raw_address = MISSING
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

        else:

            data_json = loc_dom.xpath(
                '//script[contains(text(), "var dataLayer")]/text()'
            )
            data_json = "".join(data_json)
            data_json = data_json.split("var dataLayer =")[-1].strip()
            data_json = json.loads(data_json)
            # logger.info(f"Data: {data_json}")
            locator_domain = DOMAIN
            location_name = data_json["prop_name"]
            logger.info(f"Location Name: {location_name}")

            address_raw = "".join(
                loc_dom.xpath('//div[@class="getting-here__left-body"]/p[2]/text()')
            ).strip()
            address_raw = address_raw.replace(
                "6700 North Gaylord Rockies Boulevard,Aurora 80019 Colorado USA",
                "6700 North Gaylord Rockies Boulevard, Aurora Colorado 80019 USA",
            )
            logger.info(f"Address Raw: {address_raw}")

            # address = "".join(address).strip()
            pai = parse_address_intl(address_raw)

            street_address = pai.street_address_1
            street_address = street_address if street_address else MISSING
            logger.info(f"Street Address: {street_address}")

            city = pai.city
            city = city if city else MISSING
            logger.info(f"City: {city}")

            state = pai.state
            state = state if state else MISSING
            logger.info(f"State: {state}")

            zip_postal = pai.postcode
            zip_postal = zip_postal if zip_postal else MISSING
            logger.info(f"Zip Code: {zip_postal}")

            country_code = data_json["site_id"]
            country_code = country_code if country_code else MISSING
            logger.info(f"Country Code: {country_code}")

            store_number = MISSING

            # Phone
            try:
                phone = loc_dom.xpath('//a[contains(@href, "tel:")]/text()')[0]
            except:
                try:
                    phone = loc_dom.xpath('//a[contains(@href, "tel:")]/text()')[1]
                except:
                    phone = MISSING

            location_type = data_json["prop_brand_name"] + " - Marriott"
            logger.info(f"Location Type: {location_type}")

            lat_lng = data_json["prop_address_lat_long"]
            latitude = lat_lng.split(",")[0]
            longitude = lat_lng.split(",")[-1]
            logger.info(f"(Latitude: {latitude} | Longitude: {longitude}")
            hours_of_operation = MISSING
            raw_address = address_raw if address_raw else MISSING
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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
