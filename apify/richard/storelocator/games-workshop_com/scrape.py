import time
import random
import tenacity
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from tenacity import retry, stop_after_attempt

locator_domain = "https://www.games-workshop.com/"
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)

api_url = "https://www.games-workshop.com/en-GB/store/fragments/resultsJSON.jsp?latitude=51.5072178&radius=100&longitude=-0.1275862"
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    "X-Requested-With": "XMLHttpRequest",
    "Connection": "keep-alive",
    "Referer": "https://www.games-workshop.com/en-US//store/storefinder.jsp",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}


@retry(stop=stop_after_attempt(10), wait=tenacity.wait_fixed(5))
def get_response():
    with SgRequests() as http:
        response = http.get(api_url, headers=headers)
        time.sleep(random.randint(3, 7))
        if response.status_code == 200:
            log.info(f"HTTP STATUS Return: {response.status_code}")
            return response
        raise Exception(f"HTTP Error Code: {response.status_code}")


def fetch_data(sgw: SgWriter):

    r = get_response()
    js = r.json()["locations"]
    for j in js:

        page_url = f'https://www.games-workshop.com/en-US/{j.get("seoUrl")}'
        location_name = j.get("name")
        street_address = j.get("address1")
        postal = j.get("postalCode")
        country_code = j.get("country")
        city = j.get("city")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        phone = j.get("telephone")
        store_number = (
            str(j.get("id")).replace("store-gb-", "").replace("UK.C000", "").strip()
        )
        location_type = j.get("type")

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
