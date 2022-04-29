# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "primeeye.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Accept": "application/json",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZWdTY2hlZHVsZXIiLCJqdGkiOiI1NjMxNjdkYy1jZmI4LTRlZTgtOTJmYy00ZjRjYjQ4MzEzYzMiLCJpYXQiOjE2NDk2MDcwMDQsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL25hbWVpZGVudGlmaWVyIjoiZGFlMmJlYzEtODllYy00YjBjLWFiMzEtYzFjZmJiOGVjMjRjIiwiaHR0cDovL3NjaGVtYXMueG1sc29hcC5vcmcvd3MvMjAwNS8wNS9pZGVudGl0eS9jbGFpbXMvbmFtZSI6ImFlZ1NjaGVkdWxlciIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvcm9sZSI6WyJTY2hlZHVsaW5nX1VzZXIiLCJTY2hlZHVsaW5nX1VzZXIiLCJTY2hlZHVsaW5nX1VzZXIiXSwibmJmIjoxNjQ5NjA3MDA0LCJleHAiOjE2NTQ3OTEwMDQsImlzcyI6Imh0dHA6Ly9BY3VpdHlVbml2ZXJzYWwuY29tIiwiYXVkIjoiRGVtb0F1ZGllbmNlIn0.M22sflSXktvxYBcnabshZNsDLhUptBLNvh8pw0aQRL0",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Origin": "https://scheduling.aegvision.com",
    "Referer": "https://scheduling.aegvision.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}


params = (
    ("lat", "0"),
    ("lng", "0"),
    ("brandId", "88"),
    ("businessUnitId", "40"),
)


def fetch_data():
    # Your scraper here

    api_url = "https://aeg.acuityeyecaregroup.com:8006/api/Store/GetNearbyStoresv3"

    with SgRequests() as session:
        api_res = session.get(api_url, headers=headers, params=params)
        json_res = json.loads(api_res.text)
        stores = json_res["Data"]["stores"]

        for store in stores:

            locator_domain = website

            location_name = store["office"]
            if "Primary Eye Care Centers" not in location_name:
                continue
            page_url = (
                "https://eyecarespecialtiesil.com/primary-eye-care-center/{}/".format(
                    location_name.split("-")[1].strip().replace(" ", "-").strip()
                )
            )

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
