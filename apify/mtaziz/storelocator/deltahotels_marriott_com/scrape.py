from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
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


DOMAIN = "deltahotels.marriott.com"
URL_LOCATION = "https://www.marriott.com/hotel-search.mi"

logger = SgLogSetup().get_logger("deltahotels_marriott_com")

headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def removekey(d, key):
    """
    There is an item at the end of dict and that dict contains -
    the speical character "_" in key, thererefore to parse it
    properly, this func will remove that key and value.
    """
    r = dict(d)
    del r[key]
    return r


def get_state_country_submit_search_urls():
    """
    This returns the list of URLs against each country across the world including all states in the US.
    It is found that if we load more than 10 pages with the default records of 40 per page, some pages might have less than 40.
    This is one of the issues that we experience.
    This needs to be tested and find a way to fix.
    """
    session = SgRequests()
    r_count = session.get(URL_LOCATION, headers=headers)
    time.sleep(30)
    sel_count = html.fromstring(r_count.text, "lxml")
    lis = sel_count.xpath(
        '//nav[@class="l-pos-relative m-navigation m-navigation-white"]/ul/li'
    )
    count_data_list = []
    for a in lis:
        b = a.xpath("./a/@data-detail")
        b = "".join(b)
        c = json.loads(b)
        d = removekey(c, "_")
        if "US" in d.keys():
            e = removekey(d["US"]["state"], "_")
            for i in e.items():
                country_code = i[0]
                country_label = "US"
                href = "https://www.marriott.com" + i[1]["href"]
                count = i[1]["count"]
                location = i[1]["location"]
                row = [country_code, country_label, href, count, location]
                count_data_list.append(row)
        else:
            for j in d.items():
                country_code = j[0]
                country_label = j[1]["countryLabel"]
                href = "https://www.marriott.com" + j[1]["href"]
                count = j[1]["count"]
                location = j[1]["location"]
                row = [country_code, country_label, href, count, location]
                count_data_list.append(row)

    urls_submitsearch = []
    for i in count_data_list:
        urls_submitsearch.append(i[2])
    urls_submitsearch = [url.replace(" ", "%20") for url in urls_submitsearch]

    # If view = map  is not set, the page source won't contain the data
    # In another word, there are two views, the one is list view which does -
    # does not return the data that we need but "map view " returns all the data that we need

    urls_submitsearch = [url + "&view=map" for url in urls_submitsearch]
    return urls_submitsearch


# Get the cookies from URL LOCATION
with SgChrome(
    executable_path=ChromeDriverManager().install(), is_headless=True
) as driver:
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


def fetch_data():
    state_country_submit_search_urls = get_state_country_submit_search_urls()
    total = 0
    for idx, url_base_city_state in enumerate(state_country_submit_search_urls[0:]):
        page_number_second = 1
        url_base_findHotels = "https://www.marriott.com/search/findHotels.mi"
        logger.info(f"Pulling the data from >> [{idx}] : {url_base_city_state} ")
        path2 = url_base_city_state.replace("https://www.marriott.com", "")
        headers_path_ak = {
            "authority": "www.marriott.com",
            "method": "GET",
            "path": path2,
            "scheme": "https",
            "cookie": cookies_string,
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        }
        session = SgRequests()

        r1 = session.get(url_base_city_state, headers=headers_path_ak)
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
                            logger.info(f"Data Property: {data_property}")
                            page_url = "https://www.marriott.com/hotels/travel/" + str(
                                slug
                            )
                            location_name = data_property["hotelName"]
                            street_address = (
                                location.xpath(
                                    './/div[contains(@class, "m-hotel-address")]/@data-address-line1'
                                )[0]
                                or SgRecord.MISSING
                            )
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
                        r_chicago = session.get(
                            url_base_findHotels_custom,
                            headers=headers_pagination_enabled,
                        )
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
                            logger.info(f"Data Property: {data_property}")
                            page_url = "https://www.marriott.com/hotels/travel/" + str(
                                slug
                            )
                            location_name = data_property["hotelName"]
                            street_address = (
                                location.xpath(
                                    './/div[contains(@class, "m-hotel-address")]/@data-address-line1'
                                )[0]
                                or SgRecord.MISSING
                            )
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
                    logger.info(f"Data Property: {data_property}")
                    page_url = "https://www.marriott.com/hotels/travel/" + str(slug)
                    location_name = data_property["hotelName"]
                    street_address = (
                        location.xpath(
                            './/div[contains(@class, "m-hotel-address")]/@data-address-line1'
                        )[0]
                        or SgRecord.MISSING
                    )
                    city = location.xpath("./@data-city")[0] or SgRecord.MISSING
                    state = location.xpath("./@data-statecode")[0] or SgRecord.MISSING
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
                    logger.info(f"Latitude: {latitude} | Longitude: {longitude}")
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
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
