from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import SearchableCountries, DynamicZipSearch

import tenacity
from tenacity import retry, stop_after_attempt
from sglogging import sglog

logger = sglog.SgLogSetup().get_logger(logger_name="harristeeterpharmacy.com")


@retry(stop=stop_after_attempt(10), wait=tenacity.wait_fixed(5))
def get_response(api_url):
    with SgRequests() as http:
        response = http.get(api_url, headers=headers)
        logger.info(f"HTTP STATUS Return: {response.status_code}")
        if response.status_code == 200:
            return response
        raise Exception(f"HTTP Error Code: {response.status_code}")


def fetch_data(sgw: SgWriter):
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=10
    )

    for _zip in search:
        api = f"https://www.harristeeterpharmacy.com/atlas/v1/stores/v1/search?filter.query={_zip}"
        r = session.get(api, headers=headers)
        response_status = r.status_code
        logger.info(f"Page: {api} => Response: {response_status}")
        if response_status != 200:
            r = get_response(api)

        js = r.json()["data"]["storeSearch"]["results"]

        for j in js:
            location_name = j.get("vanityName")
            part = j.get("divisionNumber")
            store_number = j.get("storeNumber")
            page_url = f"https://www.harristeeterpharmacy.com/stores/details/{part}/{store_number}"

            p = j.get("pharmacy") or {}
            if not p:
                continue

            try:
                a = j["address"]["address"]
            except:
                a = dict()

            street = a.get("addressLines") or []
            street_address = ", ".join(street)
            city = a.get("cityTown")
            state = a.get("stateProvince")
            postal = a.get("postalCode")
            country = a.get("countryCode")

            location_type = j.get("banner")
            phone = p.get("phoneNumber")
            loc = j.get("location") or {}
            latitude = loc.get("lat")
            longitude = loc.get("lng")

            _tmp = []
            hours = p.get("formattedHours") or []
            for h in hours:
                day = h.get("displayName")
                inter = h.get("displayHours")
                _tmp.append(f"{day}: {inter}")

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country,
                store_number=store_number,
                location_type=location_type,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.harristeeterpharmacy.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "X-Sec-Clge-Req-Type": "ajax",
        "X-Kroger-Channel": "WEB",
        "x-call-origin": '{"component":"store search","page":"store search"}',
        "x-dtreferer": "https://www.harristeeterpharmacy.com/stores/search?selectedStoreFilters=Pharmacy&hash=Pharmacy",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Referer": "https://www.harristeeterpharmacy.com/stores/search?searchText=75022&selectedStoreFilters=Pharmacy",
        "Connection": "keep-alive",
        "TE": "trailers",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)
