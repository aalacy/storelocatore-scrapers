from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from sglogging import SgLogSetup
from tenacity import retry, stop_after_attempt
import json
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger(logger_name="jamba_com")
MISSING = SgRecord.MISSING
DOMAIN = "jamba.com"
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "MMozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
}

PAGE_LIMIT = 50


def build_api_endpoint_urls():
    urls = []
    for offset in range(0, 850, 50):
        query_id = "f773d534-29cd-4f85-b013-3077d946aec9"
        part2 = f"&referrerPageUrl=https%3A%2F%2Flocations.jamba.com%2Fsearch&source=STANDARD&queryId={query_id}&jsLibVersion=v1.9.2"
        api_endpoint_url = f"https://liveapi.yext.com/v2/accounts/me/answers/vertical/query?experienceKey=jamba-answers&api_key=7425eae4ff5d283ef2a3542425aade29&v=20190101&version=PRODUCTION&locale=en&input=&verticalKey=restaurants&limit={PAGE_LIMIT}&offset={offset}{part2}"
        urls.append(api_endpoint_url)
    return urls


@retry(stop=stop_after_attempt(3))
def get_response(http, urlnum, url):
    logger.info(f"[{urlnum}] Pulling the data from: {url}")
    r = http.get(url, headers=HEADERS)
    if r.status_code == 200:
        logger.info(f"HTTP Status Code: {r.status_code}")
        return r
    raise Exception(f"{urlnum} : {url} >> Temporary Error: {r.status_code}")


def get_hoo_new(urlnum, i100, _):
    hours_of_operation = ""
    try:
        l = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]

        c_store_notification_banner = _["data"].get("c_storeNotificationBanner")
        if c_store_notification_banner is not None:
            hours_of_operation = c_store_notification_banner
        else:
            data_hours = _["data"]["hours"]
            days_hours_start_end = []
            for i in l:
                data_hours_days = data_hours[i]
                if data_hours_days:
                    if "openIntervals" in data_hours_days:
                        data_hours_days_openintervals = data_hours_days["openIntervals"]
                        mons = data_hours_days_openintervals[0]["start"]
                        mone = data_hours_days_openintervals[0]["end"]
                        daytime = f"{i.capitalize()} {mons} - {mone}"
                        days_hours_start_end.append(daytime)
            hours_of_operation = "; ".join(days_hours_start_end)
    except Exception as e:
        logger.info(f"Fix {e} - {urlnum} ")
        hours_of_operation = MISSING

    return hours_of_operation


def fetch_records(http: SgRequests):
    try:
        api_endpoint_urls = build_api_endpoint_urls()
        for urlnum, url in enumerate(api_endpoint_urls[0:]):
            r = get_response(http, urlnum, url)
            d = json.loads(r.text)
            json_data = d["response"]["results"]
            for idx1, _ in enumerate(json_data):
                locator_domain = DOMAIN
                page_url = ""
                if "c_baseURL" in _["data"]:
                    page_url = _["data"]["c_baseURL"]
                else:
                    page_url = MISSING
                location_name = _["data"]["c_pagesMetaData"]["pageTitle"] or MISSING
                location_name = location_name.split("|")[0]
                location_name = location_name.strip() if location_name else MISSING
                add = _["data"]["address"]
                street_address = add["line1"] or MISSING
                city = add["city"] or MISSING
                state = add["region"] or MISSING
                zip_postal = add["postalCode"] or MISSING
                country_code = add["countryCode"] or MISSING
                phone = ""
                try:
                    phone = _["data"]["mainPhone"] or MISSING
                except:
                    phone = SgRecord.MISSING
                store_number = _["data"]["id"].replace("-Jamba", "")
                location_type = _["data"]["type"] or MISSING
                ll = _["data"]["yextDisplayCoordinate"]
                latitude = ll["latitude"] or MISSING
                longitude = ll["longitude"] or MISSING
                try:
                    hours_of_operation = get_hoo_new(urlnum, idx1, _)
                except Exception as e:
                    logger.info(f" {idx1} | {e} | {page_url} | {_['data']}")

                raw_address = MISSING
                yield SgRecord(
                    page_url=page_url,
                    locator_domain=locator_domain,
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
    except Exception as e:
        raise Exception(f" Please fix {e}")


def scrape():
    count = 0
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
        with SgRequests() as http:
            records = fetch_records(http)
            for rec in records:
                writer.write_row(rec)
                count = count + 1
    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
