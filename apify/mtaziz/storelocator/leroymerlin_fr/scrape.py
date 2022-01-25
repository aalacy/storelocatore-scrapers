from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from concurrent.futures import ThreadPoolExecutor, as_completed
import ssl


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

DOMAIN = "leroymerlin.fr"
MISSING = SgRecord.MISSING
logger = SgLogSetup().get_logger("leroymerlin_fr")
MAX_WORKERS = 5

headers = {
    "accept": "application/json, text/plain, */*",
    "referer": "https://www.leroymerlin.fr/",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_records(store_num, sgw: SgWriter):
    try:
        api_url = f"https://api.woosmap.com/stores/{store_num}?key=woos-47262215-fc76-3bd2-8e0d-d8fda2544349"
        http = SgRequests()
        r = http.get(api_url, headers=headers)
        if r.status_code == 404:
            return
        if r.status_code == 200:
            logger.info(f"HTTP Success Code: {r.status_code} for {store_num}")
            data = r.json()
            props = data["properties"]
            opening_hours_usual = props["opening_hours"]["usual"]
            dates = {
                "1": "Monday",
                "2": "Tuesday",
                "3": "Wednesday",
                "4": "Thursday",
                "5": "Friday",
                "6": "Saturday",
                "7": "Sunday",
            }
            hours_of_operation = ""
            try:
                hours = []
                for k, ohu in opening_hours_usual.items():
                    weekday = dates[k] + " " + ohu[0]["start"] + " - " + ohu[0]["end"]
                    hours.append(weekday)
                hours_of_operation = "; ".join(hours)
            except:
                hours_of_operation = MISSING
            logger.info(
                f"Location Name: [<<< {props['name']} for store_id - {store_num} >>>] "
            )  # noqa

            row = SgRecord(
                page_url=props["contact"]["website"] or MISSING,
                location_name=props["name"],
                street_address=", ".join(props["address"]["lines"]) or MISSING,
                city=props["address"]["city"],
                state=MISSING,
                zip_postal=props["address"]["zipcode"] or MISSING,
                country_code=props["address"]["country_code"] or MISSING,
                store_number=props["store_id"] or MISSING,
                phone=props["contact"]["phone"],
                location_type=SgRecord.MISSING,
                latitude=data["geometry"]["coordinates"][0] or MISSING,
                longitude=data["geometry"]["coordinates"][1] or MISSING,
                locator_domain="leroymerlin.fr",
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)
    except Exception as e:
        logger.info(
            f"Please fix FetchRecordsError: << {e} >> encountered at {store_num}"
        )  # noqa


def fetch_data(sgw: SgWriter):
    # This 6_concept is not numeric, therefore, better to handle it manually
    # All the stores ID lies within a range of 1 - 300
    # We will try to get all stores within 1 - 310.
    # If the HTTP request does not happen to be successful with 200,
    # it would return, 404 and we would ignore those stores as those don't exist.
    # We will save those that have HTTP success code 200
    store_id_custom = ["6_concept"]
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task = [
            executor.submit(fetch_records, store_num, sgw)
            for store_num in range(1, 310)
        ]
        tasks.extend(task)
        task_concept = [
            executor.submit(fetch_records, store_num, sgw)
            for store_num in store_id_custom
        ]
        tasks.extend(task_concept)
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
