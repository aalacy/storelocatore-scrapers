# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "repsolmove.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "repsolmove.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    with SgRequests() as session:
        stores_req = session.get(
            "https://repsolmove.com/localizador-es",
            headers=headers,
        )
        json_str = (
            stores_req.text.split(':initial-data="')[1].strip().split(']"')[0].strip()
            + "]"
        )
        stores = json.loads(json_str.replace("&quot;", '"').strip())

        for store in stores:
            locator_domain = website
            page_url = "https://repsolmove.com/localizador-es"

            location_name = store["name"]
            locator_domain = website

            location_type = "<MISSING>"

            street_address = store["address"]
            raw_address = street_address
            city = store["town"]
            if city:
                raw_address = raw_address + ", " + city
            state = store["province"]
            if state:
                raw_address = raw_address + ", " + state
            zip = store["postalCode"]
            if zip:
                raw_address = raw_address + ", " + zip
            country_code = "PT"

            phone = store["phone"]
            hours_list = []
            try:
                hours = store["timetable"]
                for hour in hours:
                    day = hour["day"]
                    if len(hour["hours"].split(",")) == 4:
                        time = (
                            hour["hours"].split(",")[0].strip()
                            + " - "
                            + hour["hours"].split(",")[-1].strip()
                        )
                    else:
                        time = hour["hours"]

                    hours_list.append(day + ":" + time)
            except:
                pass

            hours_of_operation = "; ".join(hours_list).strip()
            store_number = store["id"]
            latitude = store["coordinates"]["y"]
            longitude = store["coordinates"]["x"]

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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STATE,
                    SgRecord.Headers.ZIP,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
