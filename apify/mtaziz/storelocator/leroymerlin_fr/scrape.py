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

headers_fr = {
    "accept": "application/json, text/plain, */*",
    "referer": "https://www.leroymerlin.fr/",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}

headers_it = {
    "accept": "application/json, text/plain, */*",
    "referer": "https://www.leroymerlin.it/",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_records_fr(store_num, sgw: SgWriter):
    try:
        api_url = f"https://api.woosmap.com/stores/{store_num}?key=woos-47262215-fc76-3bd2-8e0d-d8fda2544349"
        http = SgRequests()
        r = http.get(api_url, headers=headers_fr)
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
                    if ohu:
                        start = ohu[0]["start"]
                        end = ohu[0]["end"]
                        weekday = dates[k] + " " + start + " - " + end
                        hours.append(weekday)
                    else:
                        weekday = dates[k] + " " + "Closed"
                        hours.append(weekday)
                hours_of_operation = "; ".join(hours)
            except Exception as e:
                hours_of_operation = MISSING
                logger.info(
                    f"Fix HoursOfOperationError: << {e} >> at {opening_hours_usual}"
                )  # noqa

            logger.info(
                f"Location Name: [<<< {props['name']} for store_id - {store_num} >>>] "
            )  # noqa

            sta = ""
            add_lines = props["address"]["lines"]
            if add_lines:
                if len(add_lines) > 1:
                    sta = add_lines[0] + ", " + add_lines[1]
                else:
                    sta = ", ".join(add_lines)
            else:
                sta = MISSING

            add_lines_raw = ", ".join(props["address"]["lines"])

            # City
            city = props["address"]["city"] or MISSING
            zip_postal = props["address"]["zipcode"] or MISSING
            country_code = props["address"]["country_code"] or MISSING

            # Raw Address
            raw_address = ""
            if props["address"]["lines"]:
                raw_address = add_lines_raw
                if MISSING not in add_lines_raw:
                    raw_address = add_lines_raw
                    if MISSING not in city:
                        raw_address = raw_address + ", " + city
                        if MISSING not in zip_postal:
                            raw_address = raw_address + ", " + zip_postal
                            if MISSING not in country_code:
                                raw_address = raw_address + ", " + country_code
                            else:
                                raw_address = raw_address
                        else:
                            raw_address = raw_address
                    else:
                        raw_address = raw_address
                else:
                    raw_address = add_lines_raw
            else:
                raw_address = MISSING

            raw_address = raw_address.replace(", ,", ", ")
            raw_address = " ".join(raw_address.split())
            raw_address = raw_address.strip().lstrip(",").strip()

            sta = " ".join(sta.split())
            sta = sta.rstrip(",")
            store_number = ""
            store_number = props["store_id"] or MISSING

            if store_number == "6_concept":
                store_number = MISSING

            row = SgRecord(
                page_url=props["contact"]["website"] or MISSING,
                location_name=props["name"],
                street_address=sta,
                city=city,
                state=MISSING,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=store_number,
                phone=props["contact"]["phone"],
                location_type=SgRecord.MISSING,
                latitude=data["geometry"]["coordinates"][0] or MISSING,
                longitude=data["geometry"]["coordinates"][1] or MISSING,
                locator_domain="leroymerlin.fr",
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )

            sgw.write_row(row)
    except Exception as e:
        logger.info(
            f"Please fix FetchRecordsError: << {e} >> encountered at {store_num}"
        )  # noqa


def fetch_records_it(store_num, sgw: SgWriter):
    try:
        api_url = f"https://api.woosmap.com/stores/{store_num}?key=woos-ba374f5b-61c2-3643-a86b-a7e67f611a52"
        http = SgRequests()
        r = http.get(api_url, headers=headers_it)
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
                    if ohu:
                        start = ohu[0]["start"]
                        end = ohu[0]["end"]
                        weekday = dates[k] + " " + start + " - " + end
                        hours.append(weekday)
                    else:
                        weekday = dates[k] + " " + "Closed"
                        hours.append(weekday)
                hours_of_operation = "; ".join(hours)
            except Exception as e:
                hours_of_operation = MISSING
                logger.info(
                    f"Fix HoursOfOperationError: << {e} >> at {opening_hours_usual}"
                )  # noqa

            logger.info(
                f"Location Name: [<<< {props['name']} for store_id - {store_num} >>>] "
            )  # noqa

            sta = ""
            add_lines = props["address"]["lines"]
            if add_lines:
                if len(add_lines) > 1:
                    sta = add_lines[0] + ", " + add_lines[1]
                else:
                    sta = ", ".join(add_lines)
            else:
                sta = MISSING

            add_lines_raw = ", ".join(props["address"]["lines"])

            # City
            city = props["address"]["city"] or MISSING
            zip_postal = props["address"]["zipcode"] or MISSING
            country_code = props["address"]["country_code"] or MISSING

            # Raw Address
            raw_address = ""
            if props["address"]["lines"]:
                raw_address = add_lines_raw
                if MISSING not in add_lines_raw:
                    raw_address = add_lines_raw
                    if MISSING not in city:
                        raw_address = raw_address + ", " + city
                        if MISSING not in zip_postal:
                            raw_address = raw_address + ", " + zip_postal
                            if MISSING not in country_code:
                                raw_address = raw_address + ", " + country_code
                            else:
                                raw_address = raw_address
                        else:
                            raw_address = raw_address
                    else:
                        raw_address = raw_address
                else:
                    raw_address = add_lines_raw
            else:
                raw_address = MISSING
            raw_address = raw_address.replace(", ,", ", ")
            raw_address = " ".join(raw_address.split())
            sta = " ".join(sta.split())
            sta = sta.rstrip(",")

            # City Data update for the store name Bari S. Caterina
            # Bar S. Caterina store_id 26
            location_name = props["name"] or ""
            if location_name == "Bari S. Caterina":
                city = "Bari"
                sta = "Strada Santa Caterina, 17/E"
                zip_postal = "70124"

            row = SgRecord(
                page_url=props["contact"]["website"] or MISSING,
                location_name=location_name,
                street_address=sta,
                city=city,
                state=MISSING,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=MISSING,
                phone=props["contact"]["phone"],
                location_type=SgRecord.MISSING,
                latitude=data["geometry"]["coordinates"][0] or MISSING,
                longitude=data["geometry"]["coordinates"][1] or MISSING,
                locator_domain="leroymerlin.fr",
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )

            sgw.write_row(row)
    except Exception as e:
        logger.info(
            f"Please fix FetchRecordsError: << {e} >> encountered at {store_num}"
        )


def fetch_data_fr(sgw: SgWriter):
    # This 6_concept is not numeric, therefore, better to handle it manually
    # All the stores ID lies within a range of 1 - 300
    # We will try to get all stores within 1 - 310.
    # If the HTTP request does not happen to be successful with 200,
    # it would return, 404 and we would ignore those stores as those don't exist.
    # We will save those that have HTTP success code 200
    store_id_custom = ["6_concept"]
    MAX_STORE_NUM_FR = 310

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task = [
            executor.submit(fetch_records_fr, store_num, sgw)
            for store_num in range(0, MAX_STORE_NUM_FR)
        ]
        tasks.extend(task)
        task_concept = [
            executor.submit(fetch_records_fr, store_num, sgw)
            for store_num in store_id_custom
        ]
        tasks.extend(task_concept)
        for future in as_completed(tasks):
            if future.result() is not None:
                future.result()
            else:
                continue


def fetch_data_it(sgw: SgWriter):
    # This 6_concept is not numeric, therefore, better to handle it manually
    # All the stores ID in Italy lies within a range of 0 - 58
    # We will try to get all stores within 0 - 80.
    # If the HTTP request does not happen to be successful with 200,
    # it would return, 404 and we would ignore those stores as those stores don't exist.
    # We will save those that have HTTP success code 200

    MAX_STORE_NUM_IT = 80

    store_id_custom = ["6_concept"]
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task = [
            executor.submit(fetch_records_it, store_num, sgw)
            for store_num in range(20, MAX_STORE_NUM_IT)
        ]
        tasks.extend(task)
        task_concept = [
            executor.submit(fetch_records_it, store_num, sgw)
            for store_num in store_id_custom
        ]
        tasks.extend(task_concept)
        for future in as_completed(tasks):
            if future.result() is not None:
                future.result()
            else:
                continue


def scrape_fr():
    logger.info("Started")  # noqa
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        fetch_data_fr(writer)
    logger.info("Scrape France Finished")  # noqa


def scrape_it():
    logger.info("Scrape Italy Started")  # noqa
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        fetch_data_it(writer)
    logger.info("Scrape France Finished")  # noqa


if __name__ == "__main__":
    scrape_fr()
    scrape_it()
