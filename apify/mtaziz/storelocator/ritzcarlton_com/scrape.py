from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from webdriver_manager.chrome import ChromeDriverManager
from sgselenium import SgChrome
from sgrequests import SgRequests
import json
import time
from lxml import html
import re
import ssl
import tenacity
from tenacity import retry, stop_after_attempt
import random


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

MISSING = SgRecord.MISSING
DOMAIN = "ritzcarlton.com"
URL_LOCATION = "https://www.marriott.com/hotel-search.mi"
logger = SgLogSetup().get_logger("ritzcarlton_com")
headers_api = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
}


# Marriott Hotels has total 30 brands. The data for 23 brands is
# obtained from 22 API Endpoint URLs.
# Note: Marriott Hotels ( MC ) API Endpoint URL contains MC and
# MV (Marriott Vacation Club) brands as well.
# The data for 4 brands is obtained from Manual Method.
# Please see other crawler which crawls the data from 22 API ENDPOINT URLs
# with API based crawling.


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_response(url, headers_custom):
    with SgRequests() as http:
        response = http.get(url, headers=headers_custom)
        time.sleep(random.randint(3, 7))
        if response.status_code == 200:
            logger.info(f"{url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(f"{url} >> HTTP Error Code: {response.status_code}")


def get__regions_submit_search_urls():

    # This returns the list of URLs against each region across the world.
    # Regional Search URLs have been filtered followed by 7 brands those not having API ENDPOINT URLs.

    # There are 7 brands those not having API Endpoints so we have to manually scrape.
    # "BG Hotel" refers to "Bulgari Hotel"
    # "BR Hotel" refers to "Renaissance Hotel"
    # "EB Hotel" refers to "EDITION Hotel"
    # "ER Hotel" refers to "Marriott Executive Hotel"
    # "GE Hotel" refers to "Gaylord Hotel"
    # "PR Hotel" refers to "Protea Hotel"
    # "RZ Hotel" refers to "the Ritz-Carlton Hotel"

    # non-API-based marriottBrands include EB,RZ,BG,BR,GE,PR,ER".
    # non-API-based 4 brands has the tickets, these 4 brands include BR, EB, GE, RZ.

    # NOTE: Initially the scrape for 7 brands were merged in a sinlge crawler, later on,
    # it was decided to build the scrape for each brand, in this case, for Gaylord Hotel; that means,
    # This scrape returns the data for Gaylord Hotel accross the world. Above information are kept as a reference
    # to the earlier merged crawler.

    r_count = get_response(URL_LOCATION, headers_api)
    logger.info("Pulling Regional Search URLs")
    time.sleep(random.randint(20, 30))
    sel_count = html.fromstring(r_count.text, "lxml")
    lis = sel_count.xpath(
        '//nav[@class="l-pos-relative m-navigation m-navigation-white"]/ul/li'
    )
    lis = sel_count.xpath('//div/a[contains(text(), "View all hotels")]/@href')
    lis = ["https://www.marriott.com" + i for i in lis]
    lis = [i.replace("filterApplied=false", "filterApplied=true") for i in lis]

    # Filtered followed by a single brand
    # Gaylord Hotel (GE)
    lis = [i + "&" + "marriottBrands=RZ" for i in lis]

    # Replace any white space with %20
    lis = [url.replace(" ", "%20") for url in lis]

    # If view=map set, this will return all the data
    # If view=list set, this won't return all the data that we need
    lis = [url + "&view=map" for url in lis]
    return lis


def fetch_data_for_non_api_based_child_brands():
    # This scrapes the Data for Edition Hotels across the world
    total = 0
    regions_submit_search_urls = get__regions_submit_search_urls()
    with SgChrome(
        executable_path=ChromeDriverManager().install(), is_headless=True
    ) as driver:
        driver.get("https://www.marriott.com/search/findHotels.mi")
        time.sleep(random.randint(20, 40))
        for idx, url_base_city_state in enumerate(regions_submit_search_urls[0:]):
            page_number_second = 1
            url_base_findHotels = "https://www.marriott.com/search/findHotels.mi"
            logger.info(f"[{idx}] Pulling the data from >> : {url_base_city_state} ")
            driver.get(url_base_city_state)
            time.sleep(random.randint(15, 40))
            pgsrc = driver.page_source
            search_list_records_total = re.findall(
                r"search_list_records_total\":\s\d+,", pgsrc
            )
            search_list_records_total = "".join(search_list_records_total)
            search_list_records_total = search_list_records_total.replace(
                'search_list_records_total":', ""
            ).strip(",")
            logger.info(f"Number of records found: {search_list_records_total}")
            if not search_list_records_total:
                continue
            else:
                total += int(search_list_records_total)
                if int(search_list_records_total) > 40:
                    rrns = int(search_list_records_total) / 40
                    rrns_int = int(rrns)
                    rrns_int = rrns_int + 2
                    max_page_num = rrns_int
                    logger.info(
                        "Search list records found to be more than 40 => {max_page_num}, pagination required!"
                    )

                    for i in range(page_number_second, max_page_num):
                        if i == 1:
                            url_base_findHotels_custom = url_base_city_state
                            logger.info(
                                f"URL Base find Hotels Custom: {url_base_findHotels_custom} "
                            )
                            sel_chicago = html.fromstring(pgsrc, "lxml")
                            divs = sel_chicago.xpath(
                                '//div[contains(@class, "js-property-results")]/div/div/div[contains(@class, "l-row t-bg-standard-20 property-record-item")]'
                            )
                            for location in divs:
                                locator_domain = DOMAIN
                                slug = location.xpath("./@data-marsha")[0]
                                logger.info(f"[{idx}] Slug: {slug}")
                                data_property = location.xpath("./@data-property")[0]
                                data_property = json.loads(data_property)
                                logger.info(f"[{idx}] Data Property: {data_property}")
                                page_url = (
                                    "https://www.marriott.com/hotels/travel/"
                                    + str(slug)
                                )
                                location_name = data_property["hotelName"]
                                logger.info(f"[{idx}] Location Name: {location_name}")
                                street_address = (
                                    location.xpath(
                                        './/div[contains(@class, "m-hotel-address")]/@data-address-line1'
                                    )[0]
                                    or MISSING
                                )
                                logger.info(f"[{idx}] Street Address: {street_address}")

                                city = location.xpath("./@data-city")[0] or MISSING
                                state = (
                                    location.xpath("./@data-statecode")[0] or MISSING
                                )

                                zip_postal = (
                                    location.xpath(
                                        './/div[contains(@class, "m-hotel-address")]/@data-postal-code'
                                    )[0]
                                    or MISSING
                                )
                                country_code = (
                                    location.xpath(
                                        './/div[contains(@class, "m-hotel-address")]/@data-country-description'
                                    )[0]
                                    or MISSING
                                )
                                logger.info(
                                    f"Street Address: {street_address} | City: {city} | State: {state} | Zip: {zip_postal} | Country Code: {country_code}"
                                )
                                store_number = slug or MISSING
                                phone = (
                                    location.xpath(
                                        './/div[contains(@class, "m-hotel-address")]/@data-contact'
                                    )[0]
                                    or MISSING
                                )
                                phone = phone if phone else MISSING
                                location_type = (
                                    location.xpath("./@data-brand")[0] or MISSING
                                )
                                location_type = location_type + " Hotels"
                                latitude = data_property["lat"] or MISSING
                                longitude = data_property["longitude"] or MISSING
                                logger.info(
                                    f"[{idx}] Latitude: {latitude} | Longitude: {longitude}"
                                )
                                hours_of_operation = (
                                    data_property["propMarkerBedLabel"] or ""
                                )
                                raw_address = location.xpath(
                                    './/div[contains(@class, "m-hotel-address")]/text()'
                                )[0]
                                raw_address = " ".join(raw_address.split())
                                raw_address = raw_address if raw_address else MISSING
                                logger.info(f"[{idx}] Raw Address: {raw_address}")
                                logger.info(f"[{idx}] Data Property: {data_property}")
                                rec = SgRecord(
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
                                yield rec

                        if i > 1:
                            url_base_findHotels_custom = (
                                f"{url_base_findHotels}?page={i}"
                            )
                            driver.get(url_base_findHotels_custom)
                            time.sleep(random.randint(15, 30))
                            logger.info(
                                f"URL Base find Hotels Custom: {url_base_findHotels_custom} "
                            )
                            sel_chicago = html.fromstring(driver.page_source, "lxml")
                            divs = sel_chicago.xpath(
                                '//div[contains(@class, "js-property-results")]/div/div/div[contains(@class, "l-row t-bg-standard-20 property-record-item")]'
                            )
                            for location in divs:
                                locator_domain = DOMAIN
                                slug = location.xpath("./@data-marsha")[0]
                                logger.info(f"Slug: {slug}")
                                data_property = location.xpath("./@data-property")[0]
                                data_property = json.loads(data_property)
                                logger.info(f"[{idx}] Data Property: {data_property}")
                                page_url = (
                                    "https://www.marriott.com/hotels/travel/"
                                    + str(slug)
                                )
                                location_name = data_property["hotelName"]
                                logger.info(f"[{idx}] Location Name: {location_name}")
                                street_address = (
                                    location.xpath(
                                        './/div[contains(@class, "m-hotel-address")]/@data-address-line1'
                                    )[0]
                                    or MISSING
                                )
                                logger.info(f"[{idx}] Street Address: {street_address}")

                                city = location.xpath("./@data-city")[0] or MISSING
                                state = (
                                    location.xpath("./@data-statecode")[0] or MISSING
                                )
                                zip_postal = (
                                    location.xpath(
                                        './/div[contains(@class, "m-hotel-address")]/@data-postal-code'
                                    )[0]
                                    or MISSING
                                )
                                country_code = (
                                    location.xpath(
                                        './/div[contains(@class, "m-hotel-address")]/@data-country-description'
                                    )[0]
                                    or MISSING
                                )
                                logger.info(
                                    f"[{idx}] Street Address: {street_address} | City: {city} | State: {state} | Zip: {zip_postal} | Country Code: {country_code}"
                                )
                                store_number = slug or MISSING
                                logger.info(f"store_number: {store_number}")
                                phone = (
                                    location.xpath(
                                        './/div[contains(@class, "m-hotel-address")]/@data-contact'
                                    )[0]
                                    or MISSING
                                )
                                phone = phone if phone else MISSING
                                location_type = (
                                    location.xpath("./@data-brand")[0] or MISSING
                                )
                                location_type = location_type + " Hotels"
                                latitude = data_property["lat"] or MISSING
                                longitude = data_property["longitude"] or MISSING
                                logger.info(
                                    f"Latitude: {latitude} | Longitude: {longitude}"
                                )
                                hours_of_operation = (
                                    data_property["propMarkerBedLabel"] or ""
                                )
                                raw_address = location.xpath(
                                    './/div[contains(@class, "m-hotel-address")]/text()'
                                )[0]
                                raw_address = " ".join(raw_address.split())
                                raw_address = raw_address if raw_address else MISSING
                                logger.info(f"Raw Address: {raw_address}")
                                logger.info(f"Data Property: {data_property}")
                                rec = SgRecord(
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
                                yield rec

                else:
                    # No need to update referer
                    sel_chicago = html.fromstring(pgsrc, "lxml")
                    divs = sel_chicago.xpath(
                        '//div[contains(@class, "js-property-results")]/div/div/div[contains(@class, "l-row t-bg-standard-20 property-record-item")]'
                    )
                    for location in divs:
                        locator_domain = DOMAIN
                        slug = location.xpath("./@data-marsha")[0]
                        logger.info(f"slug: {slug}")
                        data_property = location.xpath("./@data-property")[0]
                        data_property = json.loads(data_property)
                        logger.info(f"[{idx}] Data Property: {data_property}")
                        page_url = "https://www.marriott.com/hotels/travel/" + str(slug)

                        location_name = data_property["hotelName"]
                        logger.info(f"[{idx}] Location Name: {location_name}")
                        street_address = (
                            location.xpath(
                                './/div[contains(@class, "m-hotel-address")]/@data-address-line1'
                            )[0]
                            or MISSING
                        )

                        logger.info(f"[{idx}] Street Address: {street_address}")

                        city = location.xpath("./@data-city")[0] or MISSING
                        logger.info(f"[{idx}] City: {city}")

                        state = location.xpath("./@data-statecode")[0] or MISSING
                        logger.info(f"[{idx}] State: {state}")

                        zip_postal = (
                            location.xpath(
                                './/div[contains(@class, "m-hotel-address")]/@data-postal-code'
                            )[0]
                            or MISSING
                        )
                        logger.info(f"[{idx}] ZipCode: {zip_postal}")

                        country_code = (
                            location.xpath(
                                './/div[contains(@class, "m-hotel-address")]/@data-country-description'
                            )[0]
                            or MISSING
                        )
                        logger.info(f"[{idx}] Country Code: {country_code}")

                        logger.info(
                            f"[{idx}] Street Address: {street_address} | City: {city} | State: {state} | Zip: {zip_postal} | Country Code: {country_code}"
                        )
                        store_number = slug or MISSING
                        logger.info(f"store_number: {store_number}")
                        phone = (
                            location.xpath(
                                './/div[contains(@class, "m-hotel-address")]/@data-contact'
                            )[0]
                            or MISSING
                        )

                        phone = phone if phone else MISSING
                        location_type = location.xpath("./@data-brand")[0] or MISSING
                        location_type = location_type + " Hotels"
                        latitude = data_property["lat"] or MISSING
                        longitude = data_property["longitude"] or MISSING
                        logger.info(
                            f"[{idx}] Latitude: {latitude} | Longitude: {longitude}"
                        )

                        hours_of_operation = data_property["propMarkerBedLabel"] or ""
                        raw_address = location.xpath(
                            './/div[contains(@class, "m-hotel-address")]/text()'
                        )[0]
                        raw_address = " ".join(raw_address.split())
                        raw_address = raw_address if raw_address else MISSING
                        logger.info(f"Raw Address: {raw_address}")
                        logger.info(f"Data Property: {data_property}")
                        rec = SgRecord(
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
                        yield rec
        logger.info(f"Records Found per Country or State: {total}")
    logger.info(f"Total Records: {total}")


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                }
            )
        )
    ) as writer:
        results = fetch_data_for_non_api_based_child_brands()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
