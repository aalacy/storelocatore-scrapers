from datetime import datetime as dt
from tenacity import retry, stop_after_attempt
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl
from urllib.parse import urlparse

logger = SgLogSetup().get_logger("papajohns_es")
DOMAIN = "papajohns.es"
MISSING = SgRecord.MISSING
API_ENDPOINT_URLS = [
    "https://api.new.papajohns.es/v1/stores?latitude=40.4167754&longitude=-3.7037902",
    "https://api.papajohns.cl/v1/stores?latitude=-41.468917&longitude=-72.94113639999999",
    "https://api.papajohns.cr/v1/stores?latitude=9.937315199999999&longitude=-84.0629919",
    "https://api.papajohns.com.gt/v1/stores?latitude=14.5947926&longitude=-90.51554999999999",
    "https://api.papajohns.com.pa/v1/stores?latitude=8.9943549&longitude=-79.52521569999999",
]

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
}


def convert_time(dtime):
    d1 = dt.strptime(dtime, "%Y-%m-%dT%H:%M:%S.%fZ")
    new_format = "%H:%M"
    hm = d1.strftime(new_format)
    return hm


@retry(stop=stop_after_attempt(3))
def get_page_count_and_store_data(http, url):
    res_data = http.get(url, headers=HEADERS).json()
    total_pages_count = res_data.get("total_pages")
    data_list = res_data.get("page")
    return total_pages_count, data_list


def get_all_api_endpoint_urls(http: SgRequests):
    start_page = 1
    API_ENDPOINT_URLS_ALL_PAGES = []
    for countrynum, api_endpoint_url in enumerate(API_ENDPOINT_URLS[0:]):
        aeu_domain = urlparse(api_endpoint_url).netloc
        logger.info(f"API-based domain: {aeu_domain}")
        aeu_path = urlparse(api_endpoint_url).path
        logger.info(f"API-based path: {aeu_path}")
        api_endpoint_url_first_page = f"{api_endpoint_url}&limit=50&page={start_page}"
        logger.info(f"API ENDPOINT URL: {api_endpoint_url_first_page}")
        total_pages, results = get_page_count_and_store_data(
            http, api_endpoint_url_first_page
        )
        if int(total_pages) > 1:
            for page_num in range(start_page, total_pages + 1):
                api_endpoint_url_custom = f"{api_endpoint_url}&limit=50&page={page_num}"
                API_ENDPOINT_URLS_ALL_PAGES.append(api_endpoint_url_custom)
        else:
            API_ENDPOINT_URLS_ALL_PAGES.append(api_endpoint_url_first_page)

        logger.info(f"Total number of pages: {total_pages}")
    return API_ENDPOINT_URLS_ALL_PAGES


def fetch_records():
    with SgRequests() as http:
        all_urls = get_all_api_endpoint_urls(http)
        for urlnum, api_endpoint_url in enumerate(all_urls[0:]):
            total_pages, data_json = get_page_count_and_store_data(
                http, api_endpoint_url
            )
            aeu_domain = urlparse(api_endpoint_url).netloc
            logger.info(f"API-based domain: {aeu_domain}")
            aeu_path = urlparse(api_endpoint_url).path
            logger.info(f"API-based path: {aeu_path}")
            for idx, _ in enumerate(data_json[0:]):
                locator_domain = aeu_domain.replace("api.new.", "").replace("api.", "")
                page_url = api_endpoint_url
                page_url = page_url if page_url else MISSING
                logger.info(f"[{idx}] page_url: {page_url}")

                location_name = _["name"]
                location_name = location_name if location_name else MISSING
                logger.info(f"[{idx}] location_name: {location_name}")

                add = _["text_address"]
                pai = parse_address_intl(add)
                street_address = pai.street_address_1
                street_address = street_address if street_address else MISSING
                logger.info(f"[{idx}] Street Address: {street_address}")

                city = pai.city
                city = city if city else MISSING
                logger.info(f"[{idx}] City: {city}")

                state = _["region"]
                state = state if state else MISSING
                logger.info(f"[{idx}] State: {state}")

                zip_postal = pai.postcode
                zip_postal = zip_postal if zip_postal else MISSING
                logger.info(f"[{idx}] Zip Code: {zip_postal}")

                country_code = aeu_domain.split(".")[-1].upper()
                logger.info(f"[{idx}] country_code: {country_code}")
                store_number = ""
                if "zendesk_id" in _:
                    store_number = _["zendesk_id"]
                else:
                    if "id" in _:
                        store_number = _["id"]
                    else:
                        store_number = MISSING
                logger.info(f"[{idx}] store_number: {store_number}")

                phone = _["phone"]
                phone = phone if phone else MISSING
                logger.info(f"[{idx}]  Phone: {phone}")

                # Location Type
                location_type = "Restaurant"
                location_type = location_type if location_type else MISSING
                logger.info(f"[{idx}] location_type: {location_type}")

                # Latitude
                latitude = _["latitude"]

                latitude = latitude if latitude else MISSING
                if latitude == str(0.0):
                    latitude = MISSING
                logger.info(f"[{idx}] lat: {latitude}")

                # Longitude
                longitude = _["longitude"]
                longitude = longitude if longitude else MISSING
                if longitude == str(0.0):
                    longitude = MISSING
                logger.info(f"[{idx}] lng: {longitude}")

                hoo = _["business_hours"]

                hoo_temp = []
                for h in hoo:
                    if h["dispatch_method"] == "in_store":
                        ot = convert_time(h["opening_time"])
                        ct = convert_time(h["closing_time"])
                        day = h["day"].capitalize()
                        formatted_hoo = f"{day} {ot} - {ct}"
                        hoo_temp.append(formatted_hoo)
                hours_of_operation = "; ".join(hoo_temp)
                logger.info(f"[{idx}] hours_of_operation: {hours_of_operation}")

                # Raw Address
                raw_address = ""
                raw_address = add
                raw_address = raw_address if raw_address else MISSING

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
    count = 0
    logger.info("Started")
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LOCATION_NAME,
                }
            )
        )
    ) as writer:
        results = fetch_records()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
