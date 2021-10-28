import json
from sgzip.dynamic import SearchableCountries, DynamicZipSearch, Grain_1_KM

from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from concurrent import futures
from sgscrape.pause_resume import CrawlStateSingleton

from sglogging import sglog
import time
from tenacity import retry, stop_after_attempt
import tenacity
import random

locator_domain = "moneypass.com"
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)
api_url = "https://locationapi.wave2.io/api/client/getlocations"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Accept": "*/*",
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    "Content-Type": "application/json; charset=UTF-8",
    "Origin": "https://moneypasswidget.wave2.io",
    "Connection": "keep-alive",
    "Referer": "https://moneypasswidget.wave2.io/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "TE": "trailers",
}


@retry(stop=stop_after_attempt(10), wait=tenacity.wait_fixed(5))
def get_response(_zip, data):
    with SgRequests() as http:
        response = http.post(api_url, headers=headers, data=json.dumps(data))
        time.sleep(random.randint(3, 7))
        if response.status_code == 200:
            log.info(f"{_zip}  >> HTTP STATUS Return: {response.status_code}")
            return response
        raise Exception(f"{_zip} >> HTTP Error Code: {response.status_code}")


def get_data(_zip, sgw: SgWriter):

    page_url = "https://www.moneypass.com/atm-locator.html"

    data = {
        "Latitude": "",
        "Longitude": "",
        "Address": f"{str(_zip)}",
        "City": "",
        "State": "",
        "Zipcode": "",
        "Country": "",
        "Action": "textsearch",
        "ActionOverwrite": "",
        "Filters": "ATMSF,ATMDP,HAATM,247ATM,",
    }

    r = get_response(_zip, data)

    js = r.json()["Features"]
    if js:
        log.debug(f"From {_zip} stores = {len(js)}")

        for j in js:
            a = j.get("Properties")
            location_name = a.get("LocationName") or "<MISSING>"
            street_address = a.get("Address") or "<MISSING>"
            city = a.get("City") or "<MISSING>"
            state = a.get("State") or "<MISSING>"
            postal = a.get("Postalcode") or "<MISSING>"
            if postal == "0":
                postal = "<MISSING>"
            country_code = a.get("Country") or "<MISSING>"
            store_number = a.get("LocationId")
            phone = "<MISSING>"
            latitude = a.get("Latitude") or "<MISSING>"
            longitude = a.get("Longitude") or "<MISSING>"
            location_type = a.get("LocationCategory") or "<MISSING>"
            hours_of_operation = (
                j.get("LocationFeatures").get("TwentyFourHours") or "<MISSING>"
            )

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
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    postals = DynamicZipSearch(
        country_codes=[SearchableCountries.JAPAN, SearchableCountries.USA],
        max_search_distance_miles=1,
        granularity=Grain_1_KM(),
    )

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in postals}
        for future in futures.as_completed(future_to_url):
            future.result()


def scrape():
    CrawlStateSingleton.get_instance().save(override=True)
    log.info(f"Start scrapping {locator_domain} ...")
    start = time.time()
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
