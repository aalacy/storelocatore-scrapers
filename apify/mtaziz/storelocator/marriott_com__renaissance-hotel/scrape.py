from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgChrome
from sgrequests import SgRequests
import json
import time
from lxml import html
import re
import ssl


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


DOMAIN = "marriott.com/renaissance-hotel"
URL_LOCATION = "https://www.marriott.com/hotel-search.mi"
logger = SgLogSetup().get_logger("marriott_com__renaissance-hotel")


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
# with API based crawling


def get__regions_submit_search_urls():

    # This returns the list of URLs against each region across the world.
    # Regional Search URLs have been filtered followed by 7 brands those not having API ENDPOINT URLs.
    #  search URL filtered Filter followed by 7

    # There are 7 brands those not having API Endpoints so we have to manually scrape
    # "BG Hotel" refers to "Bulgari Hotel"
    # "BR Hotel" refers to "Renaissance Hotel"
    # "EB Hotel" refers to "EDITION Hotel"
    # "ER Hotel" refers to "Marriott Executive Hotel"
    # "GE Hotel" refers to "Gaylord Hotel"
    # "PR Hotel" refers to "Protea Hotel"
    # "RZ Hotel" refers to "the Ritz-Carlton Hotel"

    # NOTE: We need to make sure that these 4 brands (i.e., BR, EB, GE, RZ ) individually meet
    # store count

    session = SgRequests()
    v = 0
    while True:
        v = v + 1
        try:
            r_count = session.get(URL_LOCATION, headers=headers_api)
            break
        except Exception as e:
            logger.info("")
            logger.info(e)
            if v == 5:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue

    logger.info("Pulling Regional Search URLs")
    time.sleep(30)
    sel_count = html.fromstring(r_count.text, "lxml")
    lis = sel_count.xpath(
        '//nav[@class="l-pos-relative m-navigation m-navigation-white"]/ul/li'
    )
    lis = sel_count.xpath('//div/a[contains(text(), "View all hotels")]/@href')
    lis = ["https://www.marriott.com" + i for i in lis]
    lis = [i.replace("filterApplied=false", "filterApplied=true") for i in lis]

    # Filtered followed by 7 brands
    lis = [i + "&" + "marriottBrands=EB,RZ,BG,BR,GE,PR,ER" for i in lis]

    # Replace any white space with %20
    lis = [url.replace(" ", "%20") for url in lis]

    # If view=map set, this will return all the data
    # If view=list set, this won't return all the data that we need
    lis = [url + "&view=map" for url in lis]
    return lis


# Get the cookies from URL LOCATION
with SgChrome() as driver:
    driver.get(URL_LOCATION)
    time.sleep(10)
    test_cookies_list = driver.get_cookies()
test_cookies_json = {}
for cookie in test_cookies_list:
    test_cookies_json[cookie["name"]] = cookie["value"]
cookies_string = (
    str(test_cookies_json)
    .replace("{", "")
    .replace("}", "")
    .replace("'", "")
    .replace(": ", "=")
    .replace(",", ";")
)


def fetch_data_for_7_child_brands():
    session = SgRequests()
    regions_submit_search_urls = get__regions_submit_search_urls()
    total = 0
    for idx, url_base_city_state in enumerate(regions_submit_search_urls[0:]):
        page_number_second = 1
        url_base_findHotels = "https://www.marriott.com/search/findHotels.mi"
        logger.info(f"[{idx}] Pulling the data from >> : {url_base_city_state} ")
        path2 = url_base_city_state.replace("https://www.marriott.com", "")
        headers_path_ak = {
            "authority": "www.marriott.com",
            "method": "GET",
            "path": path2,
            "scheme": "https",
            "cookie": cookies_string,
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        }

        x = 0
        while True:
            x = x + 1
            try:
                r1 = session.get(
                    url_base_city_state, headers=headers_path_ak, timeout=500
                )
                break
            except Exception as e:
                logger.info("")
                logger.info(e)
                if x == 5:
                    raise Exception(
                        "Make sure this ran with a Proxy, will fail without one"
                    )
                continue

        time.sleep(15)
        search_list_records_total = re.findall(
            r"search_list_records_total\":\s\d+,", r1.text
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
                    "Search list records found to be more than 40, pagination required!!!"
                )

                for i in range(page_number_second, max_page_num):
                    if i == 1:
                        url_base_findHotels_custom = url_base_city_state
                        logger.info(
                            f"URL Base find Hotels Custom: {url_base_findHotels_custom} "
                        )
                        sel_chicago = html.fromstring(r1.text, "lxml")
                        divs = sel_chicago.xpath(
                            '//div[contains(@class, "js-property-results")]/div/div/div[contains(@class, "l-row t-bg-standard-20 property-record-item")]'
                        )
                        for location in divs:
                            locator_domain = DOMAIN
                            slug = location.xpath("./@data-marsha")[0]
                            data_property = location.xpath("./@data-property")[0]
                            data_property = json.loads(data_property)
                            logger.info(f"[{idx}] Data Property: {data_property}")
                            page_url = "https://www.marriott.com/hotels/travel/" + str(
                                slug
                            )
                            location_name = data_property["hotelName"]
                            logger.info(f"[{idx}] Location Name: {location_name}")
                            street_address = (
                                location.xpath(
                                    './/div[contains(@class, "m-hotel-address")]/@data-address-line1'
                                )[0]
                                or SgRecord.MISSING
                            )
                            logger.info(f"[{idx}] Street Address: {street_address}")

                            city = location.xpath("./@data-city")[0] or SgRecord.MISSING
                            state = (
                                location.xpath("./@data-statecode")[0]
                                or SgRecord.MISSING
                            )

                            zip_postal = (
                                location.xpath(
                                    './/div[contains(@class, "m-hotel-address")]/@data-postal-code'
                                )[0]
                                or SgRecord.MISSING
                            )
                            country_code = (
                                location.xpath(
                                    './/div[contains(@class, "m-hotel-address")]/@data-country-description'
                                )[0]
                                or SgRecord.MISSING
                            )
                            logger.info(
                                f"Street Address: {street_address} | City: {city} | State: {state} | Zip: {zip_postal} | Country Code: {country_code}"
                            )
                            store_number = SgRecord.MISSING
                            store_number = SgRecord.MISSING
                            phone = (
                                location.xpath(
                                    './/div[contains(@class, "m-hotel-address")]/@data-contact'
                                )[0]
                                or SgRecord.MISSING
                            )
                            phone = phone if phone else SgRecord.MISSING
                            location_type = (
                                location.xpath("./@data-brand")[0] or SgRecord.MISSING
                            )
                            location_type = location_type + " Hotels"
                            latitude = data_property["lat"] or SgRecord.MISSING
                            longitude = data_property["longitude"] or SgRecord.MISSING
                            logger.info(
                                f"[{idx}] Latitude: {latitude} | Longitude: {longitude}"
                            )
                            hours_of_operation = SgRecord.MISSING
                            raw_address = location.xpath(
                                './/div[contains(@class, "m-hotel-address")]/text()'
                            )[0]
                            raw_address = " ".join(raw_address.split())
                            raw_address = (
                                raw_address if raw_address else SgRecord.MISSING
                            )
                            logger.info(f"[{idx}] Raw Address: {raw_address}")
                            logger.info(f"[{idx}] Data Property: {data_property}")
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

                    if i > 1:
                        referrer_custom = f"{url_base_findHotels}?page={i-1}"
                        url_base_findHotels_custom = f"{url_base_findHotels}?page={i}"
                        request_headers_path = url_base_findHotels_custom.replace(
                            "https://www.marriott.com", ""
                        )
                        headers_pagination_enabled = {
                            "authority": "www.marriott.com",
                            "method": "GET",
                            "scheme": "https",
                            "path": request_headers_path,
                            "accept": "application/json, text/plain, */*",
                            "accept-encoding": "gzip, deflate, br",
                            "upgrade-insecure-requests": "1",
                            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
                            "referrer": referrer_custom,
                        }

                        c = 0
                        while True:
                            c = c + 1
                            try:
                                r_chicago = session.get(
                                    url_base_findHotels_custom,
                                    headers=headers_pagination_enabled,
                                    timeout=500,
                                )
                                break
                            except Exception as e:
                                logger.info("")
                                logger.info(e)
                                if c == 5:
                                    raise Exception(
                                        "Make sure this ran with a Proxy, will fail without one"
                                    )
                                continue

                        time.sleep(15)
                        logger.info(
                            f"URL Base find Hotels Custom: {url_base_findHotels_custom} "
                        )
                        sel_chicago = html.fromstring(r_chicago.text, "lxml")
                        divs = sel_chicago.xpath(
                            '//div[contains(@class, "js-property-results")]/div/div/div[contains(@class, "l-row t-bg-standard-20 property-record-item")]'
                        )
                        for location in divs:
                            locator_domain = DOMAIN
                            slug = location.xpath("./@data-marsha")[0]
                            data_property = location.xpath("./@data-property")[0]
                            data_property = json.loads(data_property)
                            logger.info(f"[{idx}] Data Property: {data_property}")
                            page_url = "https://www.marriott.com/hotels/travel/" + str(
                                slug
                            )
                            location_name = data_property["hotelName"]
                            logger.info(f"[{idx}] Location Name: {location_name}")
                            street_address = (
                                location.xpath(
                                    './/div[contains(@class, "m-hotel-address")]/@data-address-line1'
                                )[0]
                                or SgRecord.MISSING
                            )
                            logger.info(f"[{idx}] Street Address: {street_address}")

                            city = location.xpath("./@data-city")[0] or SgRecord.MISSING
                            state = (
                                location.xpath("./@data-statecode")[0]
                                or SgRecord.MISSING
                            )
                            zip_postal = (
                                location.xpath(
                                    './/div[contains(@class, "m-hotel-address")]/@data-postal-code'
                                )[0]
                                or SgRecord.MISSING
                            )
                            country_code = (
                                location.xpath(
                                    './/div[contains(@class, "m-hotel-address")]/@data-country-description'
                                )[0]
                                or SgRecord.MISSING
                            )
                            logger.info(
                                f"[{idx}] Street Address: {street_address} | City: {city} | State: {state} | Zip: {zip_postal} | Country Code: {country_code}"
                            )
                            store_number = SgRecord.MISSING
                            store_number = SgRecord.MISSING
                            phone = (
                                location.xpath(
                                    './/div[contains(@class, "m-hotel-address")]/@data-contact'
                                )[0]
                                or SgRecord.MISSING
                            )
                            phone = phone if phone else SgRecord.MISSING
                            location_type = (
                                location.xpath("./@data-brand")[0] or SgRecord.MISSING
                            )
                            location_type = location_type + " Hotels"
                            latitude = data_property["lat"] or SgRecord.MISSING
                            longitude = data_property["longitude"] or SgRecord.MISSING
                            logger.info(
                                f"Latitude: {latitude} | Longitude: {longitude}"
                            )
                            hours_of_operation = SgRecord.MISSING
                            raw_address = location.xpath(
                                './/div[contains(@class, "m-hotel-address")]/text()'
                            )[0]
                            raw_address = " ".join(raw_address.split())
                            raw_address = (
                                raw_address if raw_address else SgRecord.MISSING
                            )
                            logger.info(f"Raw Address: {raw_address}")
                            logger.info(f"Data Property: {data_property}")
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
                # No need to update referrer
                sel_chicago = html.fromstring(r1.text, "lxml")
                divs = sel_chicago.xpath(
                    '//div[contains(@class, "js-property-results")]/div/div/div[contains(@class, "l-row t-bg-standard-20 property-record-item")]'
                )
                for location in divs:
                    locator_domain = DOMAIN
                    slug = location.xpath("./@data-marsha")[0]
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
                        or SgRecord.MISSING
                    )

                    logger.info(f"[{idx}] Street Address: {street_address}")

                    city = location.xpath("./@data-city")[0] or SgRecord.MISSING
                    logger.info(f"[{idx}] City: {city}")

                    state = location.xpath("./@data-statecode")[0] or SgRecord.MISSING
                    logger.info(f"[{idx}] State: {state}")

                    zip_postal = (
                        location.xpath(
                            './/div[contains(@class, "m-hotel-address")]/@data-postal-code'
                        )[0]
                        or SgRecord.MISSING
                    )
                    logger.info(f"[{idx}] ZipCode: {zip_postal}")

                    country_code = (
                        location.xpath(
                            './/div[contains(@class, "m-hotel-address")]/@data-country-description'
                        )[0]
                        or SgRecord.MISSING
                    )
                    logger.info(f"[{idx}] Country Code: {country_code}")

                    logger.info(
                        f"[{idx}] Street Address: {street_address} | City: {city} | State: {state} | Zip: {zip_postal} | Country Code: {country_code}"
                    )
                    store_number = SgRecord.MISSING
                    store_number = SgRecord.MISSING
                    phone = (
                        location.xpath(
                            './/div[contains(@class, "m-hotel-address")]/@data-contact'
                        )[0]
                        or SgRecord.MISSING
                    )

                    phone = phone if phone else SgRecord.MISSING
                    location_type = (
                        location.xpath("./@data-brand")[0] or SgRecord.MISSING
                    )
                    location_type = location_type + " Hotels"
                    latitude = data_property["lat"] or SgRecord.MISSING
                    longitude = data_property["longitude"] or SgRecord.MISSING
                    logger.info(
                        f"[{idx}] Latitude: {latitude} | Longitude: {longitude}"
                    )

                    hours_of_operation = SgRecord.MISSING
                    raw_address = location.xpath(
                        './/div[contains(@class, "m-hotel-address")]/text()'
                    )[0]
                    raw_address = " ".join(raw_address.split())
                    raw_address = raw_address if raw_address else SgRecord.MISSING
                    logger.info(f"Raw Address: {raw_address}")
                    logger.info(f"Data Property: {data_property}")
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
        logger.info(f"Records Found per Country or State: {total}")
    logger.info(f"Total Records: {total}")


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results_7_brands = fetch_data_for_7_child_brands()
        for rec in results_7_brands:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
