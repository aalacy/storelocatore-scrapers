from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgrequests import SgRequests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt
import tenacity
from datetime import datetime
from datetime import timedelta
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("blazepizza_com")
session = SgRequests()
MISSING = SgRecord.MISSING
MAX_WORKERS = 10
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36"
}


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(10))
def get_response(url):
    with SgRequests() as http:
        response = http.get(url, headers=headers)
        if response.status_code == 200:
            logger.info(f"{url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(f"{url} >> HTTP Error Code: {response.status_code}")


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(10))
def get_response_hours(url, params):
    with SgRequests() as http:
        response = http.get(url, headers=headers, params=params)
        if response.status_code == 200:
            logger.info(f"{url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(f"{url} >> HTTP Error Code: {response.status_code}")


def get_hours(location):
    try:
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        calendar = location.get("calendars", {}).get("calendar")
        hours = []
        if calendar and len(calendar) and len(calendar[0].get("ranges", [])):
            weekdays = calendar[0]["ranges"]
            for day in days:
                hour = next(filter(lambda hour: hour["weekday"] == day, weekdays), None)
                if hour:
                    start = hour.get("start").split(" ").pop()
                    end = hour.get("end").split(" ").pop()
                    time_range = f"{start}-{end}"
                else:
                    time_range = "Closed"

                hours.append(f"{day} {time_range}")
        else:
            hours.append("Closed")

        return "; ".join(hours) or MISSING
    except:
        pass


def fetch_records(idx, url, sgw: SgWriter):
    start = (datetime.now() + timedelta(days=-1)).strftime("%Y%m%d")
    end = (datetime.now() + timedelta(days=14)).strftime("%Y%m%d")
    logger.info(f"[{idx}] Pulling the data from {url}")
    r1 = get_response(url)
    data = r1.json()
    restaurants_list = data["data"][0]["restaurants"]
    for store_num, location in enumerate(restaurants_list):
        store_number = location.get("id")
        logger.info(f"[{idx}][{store_num}] Store Number: {store_number}")
        params = {
            "nomnom": "calendars",
            "nomnom_calendars_from": start,
            "nomnom_calendars_to": end,
        }
        url_hours_store_number = (
            f"https://nomnom-prod-api.blazepizza.com/restaurants/{store_number}"
        )
        r2 = get_response_hours(url_hours_store_number, params)
        hoo_data = r2.json()
        logger.info(f"Pulling the data from {url_hours_store_number}")
        try:
            locator_domain = "blazepizza.com"
            page_url = (
                f"https://nomnom-prod-api.blazepizza.com/restaurants/{store_number}"
            )
            location_name = location.get("name", MISSING)
            location_type = MISSING
            street_address = location.get("streetaddress").replace(
                " (Debit / Credit Only)", ""
            )
            city = location.get("city")
            state = location.get("state")
            page_url = "https://www.blazepizza.com/locations/" + state + "/" + city
            postal = location.get("zip", MISSING)
            country_code = location.get("country", MISSING)
            lat = location.get("latitude", MISSING)
            lng = location.get("longitude", MISSING)
            phone = location.get("telephone", MISSING)
            hours_of_operation = get_hours(hoo_data)
            if ":" not in hours_of_operation:
                hours_of_operation = "<MISSING>"

            item = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours_of_operation,
                raw_address=MISSING,
            )
            sgw.write_row(item)
        except Exception as e:
            logger.error(f"Please fix {e}")


def get_state_city_based_urls():
    url_all_states = []
    url_containing_state_city_based_data_uri = (
        "https://nomnom-prod-api.blazepizza.com/extras/restaurant/summary/state"
    )
    url_api_base = "https://nomnom-prod-api.blazepizza.com"
    r = get_response(url_containing_state_city_based_data_uri)
    data_uri = r.json()
    logger.info(f'Number of states: {len(data_uri["data"])}')
    total_count = 0
    for idx, duri in enumerate(data_uri["data"]):
        uri_cities = duri["cities"]
        for idx, uc in enumerate(uri_cities):
            datauri = uc["datauri"]
            url_full = f"{url_api_base}{datauri}"
            url_all_states.append(url_full)
            count_p_city = uc["count"]
            total_count += count_p_city
    logger.info(f"Total store count: {total_count}")
    return url_all_states


def fetch_data(sgw: SgWriter):
    # Get the list of URLs based on state and city
    list_of_state_urls = get_state_city_based_urls()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task = [
            executor.submit(fetch_records, idx, api_url, sgw)
            for idx, api_url in enumerate(list_of_state_urls[0:])
        ]
        tasks.extend(task)
        for future in as_completed(tasks):
            future.result()


def scrape():

    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
