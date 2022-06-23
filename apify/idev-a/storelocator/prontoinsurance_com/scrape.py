from sglogging import sglog

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="prontoinsurance.com")
headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Allow-Headers": "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With",
    "Access-Control-Allow-Methods": "GET, POST, PATCH, DELETE, PUT, OPTIONS",
    "Access-Control-Allow-Origin": "*",
    "Content-Type": "application/json",
    "Host": "www.prontoinsurance.com:3010",
    "Origin": "https://www.prontoinsurance.com",
    "Referer": "https://www.prontoinsurance.com/",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
}
locator_domain = "prontoinsurance.com"
hour_url = "https://www.prontoinsurance.com:3010/cmspages/store_hours"


def fetch_data(sgw: SgWriter):

    with SgRequests(verify_ssl=False) as session:
        found_poi = []

        search = DynamicZipSearch(
            country_codes=[SearchableCountries.USA],
            expected_search_radius_miles=50,
        )

        log.info("Running sgzip ..")
        for postcode in search:
            payload = {"Zip_code": postcode}
            base_link = "https://www.prontoinsurance.com:3010/cmspages/agentsearch"
            try:
                stores = session.post(base_link, headers=headers, json=payload).json()[
                    "agents"
                ]
            except:
                continue
            log.info(f"[{postcode}] {len(stores)} found")
            for store in stores:
                location_name = store["name"]
                link = "https://www.prontoinsurance.com/agentdetail/" + store["slug"]
                street_address = store["Address"].split("(In")[0].split(", CA")[0]
                city = store["City"].replace(",", "")
                state = store["State"]
                zip_code = store["Zip_code"]
                country_code = "US"
                store_number = store["id"]
                location_type = "<MISSING>"
                phone = store["phone"]
                latitude = store["Latitude"]
                longitude = store["Longitude"]
                search.found_location_at(float(latitude), float(longitude))
                if link in found_poi:
                    continue
                log.info(link)
                found_poi.append(link)
                payload = {"store_hours_id": store["store_hours_id"]}
                hr = session.post(hour_url, headers=headers, json=payload).json()
                hours = []
                if hr["status"] == "success":
                    _hr = hr["time"]
                    if _hr.get("MonFri"):
                        hours.append(f"Mon-Fri: {_hr['MonFri']}")
                    if _hr.get("saturday"):
                        hours.append(f"saturday {_hr['saturday']}")
                sgw.write_row(
                    SgRecord(
                        locator_domain=locator_domain,
                        page_url=link,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zip_code,
                        country_code=country_code,
                        store_number=store_number,
                        phone=phone,
                        location_type=location_type,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation="; ".join(hours),
                    )
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
