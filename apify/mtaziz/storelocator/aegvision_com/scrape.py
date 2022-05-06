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


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


API_ENDPOINT_URLS = [
    "https://scheduling.aegvision.com/?brand=17&showstorelocator=1&businessunit=6"
]
MISSING = SgRecord.MISSING
DOMAIN = "aegvision.com"
MAX_WORKERS = 5

headers = {
    "Accept": "application/json",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZWdTY2hlZHVsZXIiLCJqdGkiOiJkMDI2Y2E5Zi0xZTAzLTQ1YmEtYjUwYy1kMjBkZGEyM2MzYzYiLCJpYXQiOjE2MzQzMTQwMjIsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL25hbWVpZGVudGlmaWVyIjoiZGFlMmJlYzEtODllYy00YjBjLWFiMzEtYzFjZmJiOGVjMjRjIiwiaHR0cDovL3NjaGVtYXMueG1sc29hcC5vcmcvd3MvMjAwNS8wNS9pZGVudGl0eS9jbGFpbXMvbmFtZSI6ImFlZ1NjaGVkdWxlciIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvcm9sZSI6WyJTY2hlZHVsaW5nX1VzZXIiLCJTY2hlZHVsaW5nX1VzZXIiLCJTY2hlZHVsaW5nX1VzZXIiXSwibmJmIjoxNjM0MzE0MDIyLCJleHAiOjE2Mzk1MDE2MjIsImlzcyI6Imh0dHA6Ly9BY3VpdHlVbml2ZXJzYWwuY29tIiwiYXVkIjoiRGVtb0F1ZGllbmNlIn0.ELNdsFdzmzUqHL3wA_HUjG6pJLygYWQbQPXtV0_fs28",
    "Content-Type": "application/json",
    "Host": "aeg.acuityeyecaregroup.com:8006",
    "Origin": "https://scheduling.aegvision.com",
    "Referer": "https://scheduling.aegvision.com/",
}


logger = SgLogSetup().get_logger("aegvision_com")


@retry(stop=stop_after_attempt(1), wait=tenacity.wait_fixed(2))
def get_response(idx, url):
    with SgRequests() as http:
        response = http.get(url, headers=headers)
        if response.status_code == 200:
            logger.info(f"[{idx}] | {url} >> HTTP STATUS: {response.status_code}")
            return response


def get_api_urls():
    api_urls = []
    BRAND_ID_MIN = -2
    BRAND_ID_MAX = 130
    UNIT_ID_MIN = -2
    UNIT_ID_MAX = 50
    for brand_id in range(BRAND_ID_MIN, BRAND_ID_MAX):
        for unit_id in range(UNIT_ID_MIN, UNIT_ID_MAX):
            api_url = f"https://aeg.acuityeyecaregroup.com:8006/api/Store/GetNearbyStoresv3?lat=0&lng=0&brandId={brand_id}&businessUnitId={unit_id}&"
            api_urls.append(api_url)
    return api_urls


def fetch_records(idx, url, sgw: SgWriter):
    r = get_response(idx, url)
    if r is not None:
        logger.info(f"Pulling the data from [{idx}] : {url}")
        js = r.json()
        data = js["Data"]["stores"]
        if data:
            for idx1, _ in enumerate(data):
                hoo = _["hours"]
                hours_of_operation = ""
                try:
                    hoo = [
                        i["weekDay"] + " " + i["startTime"] + " - " + i["endTime"]
                        for i in hoo
                    ]
                    hours_of_operation = ", ".join(hoo)
                except:
                    hours_of_operation = MISSING
                logger.info(f"HOO: {hours_of_operation}")
                brandid_unitid = url.split("brandId=")[-1].split("&businessUnitId=")
                bid = brandid_unitid[0]
                uid = brandid_unitid[1].replace("&", "")
                purl = f"https://scheduling.aegvision.com/?brand={bid}&showstorelocator=1&businessunit={uid}"
                rec = SgRecord(
                    locator_domain=DOMAIN,
                    page_url=purl,
                    location_name=_["brandName"]
                    if _["brandName"] is not None
                    else MISSING,
                    street_address=_["address"]
                    if _["address"] is not None
                    else MISSING,
                    city=_["city"] if _["city"] is not None else MISSING,
                    state=_["state"] if _["state"] is not None else MISSING,
                    zip_postal=_["zip"] if _["zip"] is not None else MISSING,
                    country_code="US",
                    store_number=_["storeId"],
                    phone=_["phone"] if _["phone"] is not None else MISSING,
                    location_type=MISSING,
                    latitude=_["latitude"] if _["latitude"] is not None else MISSING,
                    longitude=_["longitude"] if _["longitude"] is not None else MISSING,
                    hours_of_operation=hours_of_operation,
                    raw_address=MISSING,
                )

                sgw.write_row(rec)


def fetch_data(sgw: SgWriter):
    api_urls_all = get_api_urls()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        task = [
            executor.submit(fetch_records, unum, url, sgw)
            for unum, url in enumerate(api_urls_all[0:])
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
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
