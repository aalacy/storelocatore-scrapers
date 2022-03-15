# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "pvseyecare.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZWdTY2hlZHVsZXIiLCJqdGkiOiJmZmYyYzAzOC0xZDUzLTQxM2QtODQ5Zi1kZWVlZjJjMGVkYzgiLCJpYXQiOjE2NDQ1MTI5NDMsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL25hbWVpZGVudGlmaWVyIjoiZGFlMmJlYzEtODllYy00YjBjLWFiMzEtYzFjZmJiOGVjMjRjIiwiaHR0cDovL3NjaGVtYXMueG1sc29hcC5vcmcvd3MvMjAwNS8wNS9pZGVudGl0eS9jbGFpbXMvbmFtZSI6ImFlZ1NjaGVkdWxlciIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvcm9sZSI6WyJTY2hlZHVsaW5nX1VzZXIiLCJTY2hlZHVsaW5nX1VzZXIiLCJTY2hlZHVsaW5nX1VzZXIiXSwibmJmIjoxNjQ0NTEyOTQzLCJleHAiOjE2NDk2OTMzNDMsImlzcyI6Imh0dHA6Ly9BY3VpdHlVbml2ZXJzYWwuY29tIiwiYXVkIjoiRGVtb0F1ZGllbmNlIn0.UQPARtvvwIaNU6RzuBpcIPbblemEqlWowVBRMy3FqPg",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "Origin": "https://scheduling.aegvision.com",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://scheduling.aegvision.com/",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
}

params = (
    ("lat", "0"),
    ("lng", "0"),
    ("brandId", "21"),
    ("businessUnitId", "-1"),
)


def fetch_data():
    # Your scraper here

    api_url = "https://aeg.acuityeyecaregroup.com:8006/api/Store/GetNearbyStoresv3"

    with SgRequests() as session:
        api_res = session.get(api_url, headers=headers, params=params)
        json_res = json.loads(api_res.text)
        log.info(json_res["Code"])
        stores = json_res["Data"]["stores"]

        for store in stores:

            locator_domain = website

            location_name = store["office"]
            if "Professional Vision Services" not in location_name:
                continue
            page_url = "https://scheduling.aegvision.com/?brand=21&showstorelocator=1&businessunit=-1"

            location_type = "<MISSING>"

            raw_address = "<MISSING>"
            street_address = store["address"]

            city = store["city"]
            state = store["state"]
            zip = str(store["zip"]).replace(".0", "").strip()

            country_code = "US"

            phone = store["phone"]

            hours = store["hours"]
            hour_list = []
            for hour in hours:
                day = hour["weekDay"]
                if hour["isClosed"] is True:
                    time = "Closed"
                else:
                    time = hour["startTime"] + " - " + hour["endTime"]
                hour_list.append(f"{day}: {time}")

            hours_of_operation = "; ".join(hour_list)
            store_number = store["storeNumber"]

            latitude, longitude = store["latitude"], store["longitude"]

            yield SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
