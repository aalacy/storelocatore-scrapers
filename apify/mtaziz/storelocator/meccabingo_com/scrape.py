from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from concurrent.futures import ThreadPoolExecutor, as_completed
import ssl
from tenacity import retry, stop_after_attempt
import tenacity
from sgpostal.sgpostal import parse_address_intl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

DOMAIN = "meccabingo.com"
MISSING = SgRecord.MISSING
logger = SgLogSetup().get_logger("meccabingo_com")  # noqa
MAX_WORKERS = 1


headers = {
    "accept": "application/json",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "referer": "https://www.meccabingo.com/bingo-clubs",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


@retry(stop=stop_after_attempt(6), wait=tenacity.wait_fixed(15))
def get_response(url):
    with SgRequests(timeout_config=600) as http:
        response = http.get(url, headers=headers)
        if response.status_code == 200:
            logger.info(f"{url} >> HTTP STATUS: {response.status_code}")  # noqa
            return response
        raise Exception(
            f"{url} Please fix GetResponseError or HttpCodeError: {response.status_code}"
        )


def identify_weekday(dow):
    weekday = ""
    if dow == 0:
        weekday = "Sunday"
    if dow == 1:
        weekday = "Monday"

    if dow == 2:
        weekday = "Tuesday"
    if dow == 3:
        weekday = "Wednesday"
    if dow == 4:
        weekday = "Thursday"
    if dow == 5:
        weekday = "Friday"
    if dow == 6:
        weekday = "Staturday"
    return weekday


def get_hoo(today_opening_times):
    hoo = ""
    dow = today_opening_times["dayOfWeek"]
    wd = identify_weekday(dow)
    start = today_opening_times["startTime"]
    end = today_opening_times["endTime"]
    if start and end:
        hoo = wd + " " + start + " - " + end
    else:
        hoo = MISSING
    return hoo


def fetch_records(num, url, sgw: SgWriter):
    try:
        logger.info(f"[{num}] Crawling From  {url}")  # noqa
        r = get_response(url)
        data_json = r.json()
        data = data_json["data"]
        for idx, _ in enumerate(data):
            page_url = ""
            slug = _["url"]
            if slug:
                page_url = f"https://www.meccabingo.com{slug}"
            else:
                page_url = MISSING
            logger.info(f"[{idx}] [ {page_url} ] crawled")  # noqa
            addraw = _["address"]
            sta = ""
            city = ""
            state = ""
            zc = ""
            if addraw:
                pai = parse_address_intl(addraw)
                if pai.street_address_1 is not None:
                    sta = pai.street_address_1
                else:
                    sta = MISSING
                if pai.city is not None:
                    city = pai.city
                else:
                    city = MISSING

                if pai.state is not None:
                    state = pai.state
                else:
                    state = MISSING

                if pai.postcode is not None:
                    zc = pai.postcode
                else:
                    zc = MISSING
            else:
                sta = MISSING
                city = MISSING
                state = MISSING
                zc = MISSING
            try:
                today_opening_time = _["todayOpeningTimes"]
                hoo = get_hoo(today_opening_time)
            except:
                hoo = MISSING

            row = SgRecord(
                page_url=page_url,
                location_name=_["name"] or MISSING,
                street_address=sta,
                city=city,
                state=state,
                zip_postal=zc,
                country_code="UK",
                store_number=MISSING,
                phone=_["clubTelephone"] or MISSING,
                location_type=MISSING,
                latitude=_["position"]["latitude"] or MISSING,
                longitude=_["position"]["longitude"] or MISSING,
                locator_domain=DOMAIN,
                hours_of_operation=hoo,
                raw_address=addraw,
            )
            sgw.write_row(row)
    except Exception as e:
        logger.info(
            f"Please fix FetchRecordsError: << {e} >> encountered at {url}"
        )  # noqa


def fetch_data(sgw: SgWriter):
    api_endpoint_url = [
        "https://www.meccabingo.com/api/v2/Clubs/ClosestByAddress?query=lon&count=100"
    ]
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task = [
            executor.submit(fetch_records, num, url, sgw)
            for num, url in enumerate(api_endpoint_url[0:])
        ]
        tasks.extend(task)

        for future in as_completed(tasks):
            if future.result() is not None:
                future.result()
            else:
                continue


def scrape():
    logger.info("Started")  # noqa
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")  # noqa


if __name__ == "__main__":
    scrape()
