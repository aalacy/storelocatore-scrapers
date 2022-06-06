import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import random
import time
from tenacity import retry, stop_after_attempt
import tenacity
from sgzip.dynamic import DynamicZipSearch, SearchableCountries, Grain_8
from concurrent.futures import ThreadPoolExecutor, as_completed


API_ENDPOINT_URLS__NONUSA = [
    "https://maps.restaurants.ihop.com/api/getAsyncLocations?template=search&level=search&search=bahrain&radius=10000",
    "https://maps.restaurants.ihop.com/api/getAsyncLocations?template=search&level=search&search=guam&radius=10000",
]


DOMAIN = "ihop.com"
logger = SgLogSetup().get_logger("ihop_com")
MISSING = SgRecord.MISSING
MAX_WORKERS = 3
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36",
}


@retry(stop=stop_after_attempt(10), wait=tenacity.wait_fixed(5))
def get_response(zipcode, url):
    with SgRequests(verify_ssl=False, proxy_country="us", timeout_config=300) as http:
        logger.info(f"Pulling content from {url} | {zipcode}")
        response = http.get(url, headers=headers)
        time.sleep(random.randint(10, 30))
        if response.status_code == 200:
            logger.info(f"[{zipcode}] | {url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(
            f"[{zipcode}] | {url} >> HTTP Error Code: {response.status_code}"
        )


def get_hours(raw_hours):
    temp_open_close = []
    hours_of_operation = ""
    tmp_js = json.loads(raw_hours.get("hours_sets:primary")).get("days", {})
    for day in tmp_js.keys():
        octime = tmp_js[day]
        if isinstance(octime, list):
            start = octime[0]["open"]
            close = octime[0]["close"]
            temp_open_close.append(f"{day} {start} - {close}")
        elif isinstance(octime, str):
            temp_open_close.append(f"{day} {octime}")
        else:
            temp_open_close.append(f"{day} {octime}")
    if temp_open_close:
        hours_of_operation = "; ".join(temp_open_close)
    else:
        hours_of_operation = MISSING
    return hours_of_operation


def fetch_records_nonusa(idx, api_url, sgw: SgWriter):
    r = get_response(idx, api_url)
    js_init = r.json()["maplist"]
    try:
        line = (
            "["
            + js_init.split('<div class="tlsmap_list">')[1].split(",</div>")[0]
            + "]"
        )
    except:
        return
    js = json.loads(line)
    js_markers = r.json()["markers"]
    for idx1, j in enumerate(js):
        page_url = ""
        store_url = j.get("url")
        country_code = j.get("country") or MISSING
        if country_code == "US" or country_code == "PR":
            page_url = store_url.replace(
                "https://restaurants.ihop.com/",
                "https://restaurants.ihop.com/en-us/",
            )

        if country_code == "CA":
            page_url = store_url.replace(
                "https://restaurants.ihop.com/",
                "https://restaurants.ihop.com/en-ca/",
            )

        if country_code == "PA":
            page_url = store_url

        if not store_url:
            page_url = MISSING

        location_name = j.get("location_name") or MISSING
        logger.info(f"[{idx1}] Location Name: {location_name}")
        street_address = f"{j.get('address_1')} {j.get('address_2')}".strip() or MISSING
        city = j.get("city") or MISSING
        state = j.get("region") or MISSING
        postal = j.get("post_code") or MISSING

        if "MX" in str(country_code):
            continue
        store_number = j.get("fid") or MISSING
        phone = j.get("local_phone") or MISSING

        latitude = js_markers[idx1].get("lat") or MISSING
        longitude = js_markers[idx1].get("lng") or MISSING
        location_type = j.get("location_type") or MISSING
        hoo = get_hours(j)
        row = SgRecord(
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
            latitude=latitude,
            longitude=longitude,
            locator_domain=DOMAIN,
            hours_of_operation=hoo,
            raw_address=MISSING,
        )

        sgw.write_row(row)


def fetch_records_america(zipcode, search, current_country, sgw: SgWriter):
    logger.info(f"PullingDataForZipcode: {zipcode}")
    RADIUS = 1000
    LIMIT = 300
    api_endpoint_url = f"https://maps.restaurants.ihop.com/api/getAsyncLocations?template=search&level=search&search={zipcode}&limit={LIMIT}&radius={RADIUS}"
    try:
        r = get_response(zipcode, api_endpoint_url)
        logger.info(f"HTTPStatus: {r.status_code}")
        js_init = r.json()["maplist"]

        line = (
            "["
            + js_init.split('<div class="tlsmap_list">')[1].split(",</div>")[0]
            + "]"
        )
        js = json.loads(line)
        js_markers = r.json()["markers"]
        logger.info(f"StoreCountRaw: {len(js_markers)}")
        for idx1, j in enumerate(js):
            page_url = ""
            store_url = j.get("url")
            country_code = j.get("country") or MISSING
            if country_code == "US" or country_code == "PR":
                page_url = store_url.replace(
                    "https://restaurants.ihop.com/",
                    "https://restaurants.ihop.com/en-us/",
                )

            if country_code == "CA":
                page_url = store_url.replace(
                    "https://restaurants.ihop.com/",
                    "https://restaurants.ihop.com/en-ca/",
                )

            if country_code == "PA":
                page_url = store_url

            if not store_url:
                page_url = MISSING

            location_name = j.get("location_name") or MISSING
            logger.info(f"[{idx1}] Location Name: {location_name}")
            street_address = (
                f"{j.get('address_1')} {j.get('address_2')}".strip() or MISSING
            )
            city = j.get("city") or MISSING
            state = j.get("region") or MISSING
            postal = j.get("post_code") or MISSING

            if "MX" in str(country_code):
                continue
            store_number = j.get("fid") or MISSING
            phone = j.get("local_phone") or MISSING

            if "(405) 275-4467 54" in phone:
                phone = "(405) 275-4467"

            if "(540) 463-3478 223" in phone:
                phone = "(540) 463-3478"

            latitude = js_markers[idx1].get("lat") or MISSING
            longitude = js_markers[idx1].get("lng") or MISSING
            logger.info(f"[{idx1}] [({latitude}, {longitude}) ]")
            location_type = j.get("location_type") or MISSING
            hoo = get_hours(j)
            row = SgRecord(
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
                latitude=latitude,
                longitude=longitude,
                locator_domain=DOMAIN,
                hours_of_operation=hoo,
                raw_address=MISSING,
            )

            sgw.write_row(row)
    except:
        logger.info(f"DataNotAvailable: {api_endpoint_url}")
        return


def fetch_data(sgw: SgWriter):
    logger.info("Started")
    # 1703 stores when 300 miles used
    search_us = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=300,
        granularity=Grain_8(),
        use_state=False,
    )
    country_us = search_us.current_country().upper()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []

        task_non_usa = [
            executor.submit(fetch_records_nonusa, idx, api_url, sgw)
            for idx, api_url in enumerate(API_ENDPOINT_URLS__NONUSA)
        ]
        tasks.extend(task_non_usa)

        task_us = [
            executor.submit(fetch_records_america, zipcode, search_us, country_us, sgw)
            for zipcode in search_us
        ]
        tasks.extend(task_us)

        for future in as_completed(tasks):
            if future.result() is not None:
                future.result()


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.PAGE_URL,
                }
            ),
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
