import json
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch

from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
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
def get_response(data):
    with SgRequests() as http:
        response = http.post(api_url, headers=headers, data=json.dumps(data))
        time.sleep(random.randint(3, 7))
        if response.status_code == 200:
            log.info(f"HTTP STATUS Return: {response.status_code}")
            return response
        raise Exception(f"HTTP Error Code: {response.status_code}")


def get_data(coord, sgw: SgWriter):
    lat, lng = coord

    page_url = "https://www.moneypass.com/atm-locator.html"

    data = {
        "Latitude": f"{lat}",
        "Longitude": f"{lng}",
        "Address": "",
        "City": "",
        "State": "",
        "Zipcode": "",
        "Country": "",
        "Action": "textsearch",
        "ActionOverwrite": "",
        "Filters": "ATMSF,ATMDP,HAATM,247ATM,",
    }

    r = get_response(data)

    js = r.json()["Features"]
    if js:
        log.debug(f"From {lat,lng} stores = {len(js)}")

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
    postals = DynamicGeoSearch(
        country_codes=[
            SearchableCountries.USA,
            SearchableCountries.JAPAN,
            SearchableCountries.BELGIUM,
            SearchableCountries.GERMANY,
            SearchableCountries.BRITAIN,
            SearchableCountries.ITALY,
        ],
        max_search_distance_miles=300,
        expected_search_radius_miles=50,
        max_search_results=100,
    )

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in postals}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    CrawlStateSingleton.get_instance().save(override=True)

    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        fetch_data(writer)
