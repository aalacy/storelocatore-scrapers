# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "rowlandspharmacy.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}

params = {
    "v": "20211005",
    "language": "en",
    "fieldMask": [
        "id",
        "identifier",
        "googlePlaceId",
        "lat",
        "lng",
        "name",
        "country",
        "city",
        "province",
        "streetAndNumber",
        "zip",
        "businessId",
        "addressExtra",
        "callToActions",
        "openingHours",
        "openNow",
        "nextOpen",
        "phone",
        "photos",
        "specialOpeningHours",
    ],
}


def fetch_data():
    # Your scraper here
    with SgRequests() as session:
        stores_req = session.get(
            "https://uberall.com/api/storefinders/bwzEvjRHRFzJjkeRduLJgHcDYens3x/locations/all",
            headers=headers,
        )
        stores = json.loads(stores_req.text)["response"]["locations"]
        for store in stores:
            locator_domain = website
            location_name = store["name"]

            street_address = store["streetAndNumber"]
            city = store["city"]
            state = store["province"]
            zip = store["zip"]
            country_code = "GB"

            store_number = store["identifier"]
            page_url = f"https://www.rowlandspharmacy.co.uk/find-local-pharmacy#!/l/{city.lower()}/{street_address.replace(' ','-').strip()}/{store_number}"

            phone = store["phone"]

            location_type = "<MISSING>"
            hours_list = []
            hours = store["openingHours"]
            for hour in hours:
                start_time_list = []
                end_time_list = []
                if hour["dayOfWeek"] == 1:
                    day = "Monday"
                if hour["dayOfWeek"] == 2:
                    day = "Tuesday"
                if hour["dayOfWeek"] == 3:
                    day = "Wednesday"
                if hour["dayOfWeek"] == 4:
                    day = "Thursday"
                if hour["dayOfWeek"] == 5:
                    day = "Friday"
                if hour["dayOfWeek"] == 6:
                    day = "Saturday"
                if hour["dayOfWeek"] == 7:
                    day = "Sunday"

                if "closed" in hour and hour["closed"] is True:
                    time = "Closed"
                else:
                    if "from1" in hour:
                        start_time_list.append(hour["from1"])
                    if "from2" in hour:
                        start_time_list.append(hour["from2"])

                    if "to1" in hour:
                        end_time_list.append(hour["to1"])
                    if "to2" in hour:
                        end_time_list.append(hour["to2"])

                    time = start_time_list[0] + " - " + end_time_list[-1]

                hours_list.append(day + ":" + time)

            hours_of_operation = ";".join(hours_list).strip()
            latitude = store["lat"]
            longitude = store["lng"]

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
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
