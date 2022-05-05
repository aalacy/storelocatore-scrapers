# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "carrxpert.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.carrxpert.com",
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://www.carrxpert.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.carrxpert.com/en/find-a-collision-repair-centre",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.carrxpert.com/en/find-a-collision-repair-centre/page/{}"
    page_no = 1
    data = {}
    data["page"] = str(page_no)
    log.info(f"pulling info from page_no: {page_no}")
    json_req = session.post(search_url.format(str(page_no)), data=data, headers=headers)
    json_data = json.loads(json_req.text)
    page_no = json_data["maxPages"]

    while True:
        data["page"] = str(page_no)
        log.info(f"pulling info from page_no: {page_no}")
        json_req = session.post(
            search_url.format(str(page_no)), data=data, headers=headers
        )
        json_data = json.loads(json_req.text)

        stores = json_data["shopList"]
        for store in stores:
            store_json = json.loads(store)

            page_url = (
                "https://www.carrxpert.com/en/dealer/" + store_json["details"]["slug"]
            )
            locator_domain = website
            location_name = store_json["details"]["nomCentre"]
            street_address = store_json["details"]["adresse"]
            city = store_json["details"]["ville"]
            state = store_json["details"]["province"]
            zip = store_json["details"]["codePostal"]

            country_code = "US"
            if zip and " " in zip:
                country_code = "CA"

            store_number = store_json["details"]["key"]
            phone = ""
            if store_json["details"]["tel"] is not None:
                phone = (
                    store_json["details"]["indTel"] + " " + store_json["details"]["tel"]
                )

            location_type = "<MISSING>"

            hours_list = []
            hours = store_json["schedule"]
            for key in hours.keys():
                if key == "1":
                    day = "Monday:"
                elif key == "2":
                    day = "Tuesday:"
                elif key == "3":
                    day = "Wednesday:"
                elif key == "4":
                    day = "Thursday:"
                elif key == "5":
                    day = "Friday:"
                elif key == "6":
                    day = "Saturday:"
                elif key == "7":
                    day = "Sunday:"

                if hours[key]["openTime"] is not None:
                    time = hours[key]["openTime"] + "-" + hours[key]["closeTime"]
                else:
                    time = "Closed"

                hours_list.append(day + time)

            hours_of_operation = "; ".join(hours_list).strip()

            latitude = store_json["location"]["latitude"]
            longitude = store_json["location"]["longitude"]

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

        if json_data["currentPage"] == json_data["maxPages"]:
            break
        else:
            page_no = page_no + 1


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
