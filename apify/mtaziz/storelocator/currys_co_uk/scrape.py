from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
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


logger = SgLogSetup().get_logger("currys_co_uk")
LOCATOR_URL = (
    "https://www.currys.co.uk/store-finder?showMap=true&horizontalView=true&isForm=true"
)
DOMAIN = "currys.co.uk"
MAX_WORKERS = 10


def fetch_records(max_count, sgw: SgWriter):
    api_url = f"https://api.currys.co.uk/store/api/stores?maxCount={max_count}&types=2in1-HS%2C2in1-MS%2C2in1-SS%2C3in1-HS%2C3in1-MS%2C3in1-SS%2CBLACK%2CCDG-HS%2CCUR-MS%2CCUR-SS%2CPCW-HS%2CPCW-SS"
    logger.info(f"Pulling the data from {api_url}")
    with SgRequests() as session:
        r = session.get(api_url)
        logger.info(f"HTTP Status: {r.status_code}")
        js = r.json()["payload"]["stores"]
        for j in js:
            street_address = j.get("address") or ""
            city = j.get("town") or ""
            state = ""
            postal = j.get("postcode") or ""
            country_code = "GB"
            store_number = j.get("id") or ""
            page_url = f"https://www.currys.co.uk/gbuk/store-finder/london/store-{store_number}"
            location_name = f"Currys PC World, {city}"
            phone = ""
            loc = j.get("location")
            latitude = loc.get("latitude") or ""
            longitude = loc.get("longitude") or ""
            location_type = ""

            _tmp = []
            days = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
            hours = j.get("standardOpeningHours") or []
            for h in hours:
                index = h.get("day") - 1
                day = days[index]
                start = h.get("from")
                close = h.get("to")
                _tmp.append(f"{day}: {start} - {close}")

            hours_of_operation = ";".join(_tmp) or ""
            item = SgRecord(
                locator_domain=DOMAIN,
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
                hours_of_operation=hours_of_operation,
                raw_address="",
            )
            sgw.write_row(item)


def fetch_data(sgw: SgWriter):
    logger.info("Started")
    max_count = ["5000"]
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task_global = [executor.submit(fetch_records, mc, sgw) for mc in max_count]
        tasks.extend(task_global)
        for future in as_completed(tasks):
            future.result()


def scrape():

    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.STREET_ADDRESS,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
