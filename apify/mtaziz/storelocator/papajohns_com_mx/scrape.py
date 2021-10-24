from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt
import tenacity
import ssl
import random
from lxml import html
import time
import json
from urllib.parse import urlparse
from sgpostal.sgpostal import parse_address_intl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


API_ENDPOINT_URLS = [
    "https://papajohns.com.mx/service/stores/general",
    "https://papajohns.pr/service/stores/general",
    "https://papajohns.com.bo/service/stores/general",
    "https://www.papajohns.ni/service/stores/general",
]
MISSING = SgRecord.MISSING
DOMAIN = "papajohns.com.mx"
MAX_WORKERS = 5

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36"
}

logger = SgLogSetup().get_logger("dominos_com")


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(2))
def get_response(idx, url):
    with SgRequests() as http:
        response = http.get(url, headers=headers)
        time.sleep(random.randint(1, 3))
        if response.status_code == 200:
            logger.info(f"[{idx}] | {url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(f"[{idx}] | {url} >> HTTP Error Code: {response.status_code}")


def get_hoo(hoo_raw):
    hours = []
    for e in hoo_raw:
        dw = e["dayOfWeek"]
        if dw == str(0):
            daytime = f'Sun: {e["startTime"]} - {e["endTime"]}'
            hours.append(daytime)
        if dw == str(1):
            daytime = f'Mon: {e["startTime"]} - {e["endTime"]}'
            hours.append(daytime)
        if dw == str(2):
            daytime = f'Tue: {e["startTime"]} - {e["endTime"]}'
            hours.append(daytime)
        if dw == str(3):
            daytime = f'Wed: {e["startTime"]} - {e["endTime"]}'
            hours.append(daytime)
        if dw == str(4):
            daytime = f'Thu: {e["startTime"]} - {e["endTime"]}'
            hours.append(daytime)
        if dw == str(5):
            daytime = f'Fri: {e["startTime"]} - {e["endTime"]}'
            hours.append(daytime)
        if dw == str(6):
            daytime = f'Sat: {e["startTime"]} - {e["endTime"]}'
            hours.append(daytime)
    return hours


def fetch_records(idx, url, sgw: SgWriter):
    try:
        r = get_response(idx, url)
        domain = urlparse(url).netloc
        datamx = json.loads(r.content)
        datamx_response = datamx["response"]
        for idx, _ in enumerate(datamx_response):
            locator_domain = urlparse(url).netloc
            ln = _["name"]
            slug = _["url"]
            page_url = f"https://{domain}/restaurant/{slug}"
            address = _["address"]
            pai = parse_address_intl(address)
            sta = pai.street_address_1 if pai.street_address_1 is not None else MISSING
            city = pai.city if pai.city is not None else MISSING
            state = pai.city if pai.city is not None else MISSING
            zc = pai.postcode if pai.postcode is not None else MISSING
            logger.info(f"address: {address}")
            phone = _["phone"]
            country_code = _["countryCode"]
            if "MEX" in country_code:
                country_code = "MX"
            if "PRI" in country_code:
                country_code = "PR"
            if "NIC" in country_code:
                country_code = "NI"
            if "BOL" in country_code:
                country_code = "BO"
            store_number = _["externalSnum"]
            location_type = MISSING
            latitude = _["latitude"]
            longitude = _["longitude"]
            api_general_store_url = f"https://{domain}/service/general-store/{slug}"
            r2 = get_response(idx, api_general_store_url)
            hoo_data = r2.json()
            hoo_schedule = hoo_data["response"][0]["schedule"]

            hours_of_operation = ""
            try:
                hours_of_operation = ", ".join(get_hoo(hoo_schedule))
            except:
                hours_of_operation = MISSING

            raw_address = address

            rec = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=ln,
                street_address=sta,
                city=city,
                state=state,
                zip_postal=zc,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )
            sgw.write_row(rec)

    except Exception as e:
        raise Exception(f" Please fix this >> {e} >> Error Encountered at {url}")


def fetch_data(sgw: SgWriter):
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        task = [
            executor.submit(fetch_records, unum, url, sgw)
            for unum, url in enumerate(API_ENDPOINT_URLS[0:])
        ]

        for future in as_completed(task):
            future.result()


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.STREET_ADDRESS,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
