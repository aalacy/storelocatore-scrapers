from sglogging import SgLogSetup
from sgselenium import SgChrome
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from datetime import datetime, timedelta
import time
import pytz

session = SgRequests()
DOMAIN = "https://www.tacocabana.com"
logger = SgLogSetup().get_logger(logger_name="tacocabana_com")
MISSING = "<MISSING>"


def get_headers(url, api_v1_ordering, headerIdent):
    with SgChrome(is_headless=True) as driver:
        driver.get(url)
        time.sleep(20)
        for r in driver.requests:
            logger.info(f"Getting Bearer Token from Path: {r.path}")
            if api_v1_ordering in r.path and r.headers[headerIdent]:
                logger.info("Bearer Token Found: Congrats!")
                return r.headers


def get_hoo(hoo, state_for_different_timezone):
    hoo_list = []
    current_date_found_at = 0
    for idx, h in enumerate(hoo):
        tz = pytz.timezone("US/Central")
        ct = datetime.now(tz=tz)
        today_date = datetime.strftime(ct, "%Y-%m-%d")
        start_time = h["start"]
        if today_date in start_time:
            current_date_found_at += idx
    logger.info(f"Current Date Id: {current_date_found_at}")
    for idx, h in enumerate(hoo):
        if idx >= current_date_found_at and idx <= current_date_found_at + 6:
            day_of_week = h["day_of_week"]
            test_start = h["start"]
            test_end = h["end"]
            start_line = test_start.split("T")[1]
            end_line = test_end.split("T")[1]
            if "NM" in state_for_different_timezone:
                start_sanitized = (
                    datetime.strptime(start_line, "%H:%M:%S+00:00") - timedelta(hours=6)
                ).strftime("%I:%M %p")

                end_sanitized = (
                    datetime.strptime(end_line, "%H:%M:%S+00:00") - timedelta(hours=6)
                ).strftime("%I:%M %p")
            else:
                start_sanitized = (
                    datetime.strptime(start_line, "%H:%M:%S+00:00") - timedelta(hours=5)
                ).strftime("%I:%M %p")

                end_sanitized = (
                    datetime.strptime(end_line, "%H:%M:%S+00:00") - timedelta(hours=5)
                ).strftime("%I:%M %p")
            hoo_sanitized = f"{day_of_week} {start_sanitized} - {end_sanitized}"
            hoo_list.append(hoo_sanitized)
    hoo_formatted = "; ".join(hoo_list)
    logger.info(f"Hours of Operation: {hoo_formatted}")
    if hoo_formatted:
        return hoo_formatted
    else:
        return MISSING


def get_all_stores_data():
    data_list = []
    url_location = "https://www.tacocabana.com/locations"
    api_url_ordering = "/v1/ordering/store-locations"
    headers = get_headers(url_location, api_url_ordering, "Authorization")
    headers = dict(headers)
    logger.info(f"Headers: {headers}")
    page_num = 1
    url_api = f"https://api.koala.fuzzhq.com/v1/ordering/store-locations/?include%5B0%5D=operating_hours&include%5B1%5D=attributes&per_page=50&page={page_num}"
    logger.info(f"URL API Endpoint: {url_api} ")
    logger.info("Pulling the count info for total number of pages")
    data_json = session.get(url_api, headers=headers, timeout=60).json()
    total_pages = data_json.get("meta").get("pagination").get("total_pages")
    logger.info(f"Total Pages Found: {total_pages}")
    page_offset = 1
    total_pages = total_pages + page_offset
    data_list.extend(data_json["data"])
    if total_pages:
        for i in range(1, total_pages):
            page_num_new = page_num + i
            url_api_new = f"https://api.koala.fuzzhq.com/v1/ordering/store-locations/?include%5B0%5D=operating_hours&include%5B1%5D=attributes&per_page=50&page={page_num_new}"
            data_json = session.get(url_api_new, headers=headers).json()
            data_list.extend(data_json["data"])
    logger.info(f"store count: {len(data_list)}")
    return data_list


def fetch_data():
    data_all = get_all_stores_data()
    location_name_menu = "https://olo.tacocabana.com/menu/"
    s = set()
    for row_num, data in enumerate(data_all):
        logger.info(f"(Data: {row_num}: {data} ")
        logger.info(f"Parsing the data at Row: {row_num}")
        # Location Name
        location_name_data = data["label"]
        location_name = location_name_data if location_name_data else MISSING

        # Page URL
        slug = data["slug"]
        page_url = f"{location_name_menu}{slug}"
        logger.info(f"[Page URL: {page_url} ]")

        # Locator Domain
        locator_domain = DOMAIN
        logger.info(f"[Location Name: {location_name} ]")

        # Address and Country Code
        street_address = data["street_address"].strip() or MISSING
        logger.info(f"[Street Address: {street_address} ]")
        city = data["city"] or MISSING
        state_data = data["cached_data"]["state"]
        state = state_data if state_data else MISSING
        zip_postal = data["zip_code"] or MISSING
        country_code = data["country"] or MISSING
        logger.info(
            f"[Street Address: {street_address} | [City: {city} | State: {state} | Zip: {zip_postal} | Country Code: {country_code}]"
        )

        store_number = data["brand_id"]
        store_number = store_number if store_number else MISSING
        logger.info(f"[Store Number: {store_number} ]")
        if "OLO" in store_number:
            continue
        if store_number in s:
            continue
        s.add(store_number)

        # Phone Number
        phone = phone = data["phone_number"] or MISSING
        logger.info(f"[Phone: {phone}]")
        # Longitude
        latitude = data["latitude"] or MISSING
        logger.info(f"[Latitude: {latitude}]")

        # Latitude
        longitude = data["longitude"] or MISSING
        logger.info(f"[Longitude: {longitude}]")

        # Location Type
        location_type = ""
        location_type = location_type if location_type else MISSING
        logger.info(f"[Location Type: {location_type}]")

        # Hours of Operation
        hoo_raw = data["operating_hours"]
        hours_of_operation = get_hoo(hoo_raw, state_data)

        # Raw Address
        raw_address = MISSING
        logger.info(f"[Raw Address: {raw_address} ]")
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
    logger.info("Scraping Started")
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
