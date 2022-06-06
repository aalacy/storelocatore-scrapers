from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries, DynamicZipSearch
from tenacity import stop_after_attempt, wait_fixed, retry
from sglogging import sglog


@retry(stop=stop_after_attempt(1), wait=wait_fixed(5))
def get_json(api):
    r = session.get(api, headers=headers)
    logger.info(f"{api}: {r}")
    js = r.json()["data"]

    return js


def fetch_data(sgw: SgWriter):
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=8
    )
    for _zip in search:
        for i in range(777):
            api = f"https://www.zales.com/store-finder?q={_zip}&page={i}"

            try:
                js = get_json(api)
            except:
                logger.info(f"{api}: ERROR!")
                js = []

            for j in js:
                _type = j.get("baseStore") or ""
                location_name = "Zales"
                location_type = "Zales"
                slug = j.get("url")
                page_url = f"https://www.zales.com{slug}?baseStore={_type}"
                if page_url.endswith("/null"):
                    page_url = SgRecord.MISSING

                street_address = f'{j.get("line1")} {j.get("line2") or ""}'.strip()
                city = j.get("town")
                state = j.get("region")
                postal = j.get("postalCode")
                country_code = "US"
                phone = j.get("phone")
                latitude = j.get("latitude")
                longitude = j.get("longitude")
                store_number = j.get("name")
                if _type == "zalesoutlet":
                    location_name = "Zales Outlet"
                    location_type = "Outlet"

                _tmp = []
                items = j.get("openings") or {}
                for k, v in items.items():
                    _tmp.append(f"{k} {v}")

                hours_of_operation = ";".join(_tmp)
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

            if len(js) < 5:
                break


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.zales.com/"
    logger = sglog.SgLogSetup().get_logger(logger_name="zales.com")
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
        "Accept": "application/json;q=0.9",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)
