import json
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch, Grain_2
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from concurrent import futures
from sglogging import sglog
import time
from tenacity import retry, stop_after_attempt
import tenacity
import random

locator_domain = "acuonline.org"
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)

api_url = "https://locationapi.wave2.io/api/client/getlocations"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    "Content-Type": "application/json; charset=UTF-8",
    "Origin": "https://03919locator.wave2.io",
    "Connection": "keep-alive",
    "Referer": "https://03919locator.wave2.io/",
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
        "Filters": "FCS,FIITM,FIATM,ATMSF,ATMDP,ESC,",
    }

    r = get_response(data)
    js = r.json()["Features"]
    log.info(f"From {lat,lng} stores found = {len(js)}")
    if js:
        for j in js:
            a = j.get("Properties")
            page_url = "https://www.acuonline.org/home/resources/locations"
            street_address = "".join(a.get("Address")).capitalize() or "<MISSING>"
            city = a.get("City") or "<MISSING>"
            state = a.get("State") or "<MISSING>"
            postal = a.get("Postalcode") or "<MISSING>"
            country_code = a.get("Country") or "<MISSING>"
            phone = a.get("Phone") or "<MISSING>"
            latitude = a.get("Latitude") or "<MISSING>"
            store_number = a.get("LocationId") or "<MISSING>"
            longitude = a.get("Longitude") or "<MISSING>"
            location_type = j.get("LocationFeatures").get("LocationType")
            location_name = a.get("LocationName")
            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            tmp = []
            for d in days:
                day = d
                try:
                    opens = a.get(f"{d}Open")
                    closes = a.get(f"{d}Close")
                    line = f"{day} {opens} - {closes}"
                    if opens == closes:
                        line = "<MISSING>"
                except:
                    line = "<MISSING>"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)
            if hours_of_operation.count("<MISSING>") == 7:
                hours_of_operation = "<MISSING>"
            hours_of_operation = hours_of_operation.replace(
                "Closed -", "Closed"
            ).strip()
            if hours_of_operation.count("Closed") == 7:
                hours_of_operation = "Closed"
            if hours_of_operation.find("<MISSING>") != -1:
                hours_of_operation = "<MISSING>"

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
    coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_results=100,
        granularity=Grain_2(),
    )

    with futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in coords}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)
