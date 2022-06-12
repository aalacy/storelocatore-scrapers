# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "fikasupply.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here

    search_url = "https://fikasupply.com/stores/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)
        json_str = (
            "".join(search_sel.xpath('//div[@class="stores-json"]/text()'))
            .strip()
            .replace("true", "True")
            .replace("false", "False")
            .replace("null", "None")
        )

        stores = eval(json_str)["features"]
        for no, store in enumerate(stores, 1):

            locator_domain = website

            page_url = search_url + store["properties"]["slug"]
            location_name = store["properties"]["name"].strip()

            location_type = store["properties"]["category"].strip()

            raw_address = "<MISSING>"

            street_address = store["properties"]["address"]

            city = store["properties"]["city"]

            state = store["properties"]["province"]

            zip = store["properties"]["postal_code"]

            country_code = store["properties"]["country"]

            phone = store["properties"]["phone"]

            hours_info = store["properties"]["hours"]
            hour_list = []
            for day in [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ]:
                opens = hours_info[day][f"{day}_hours_open"]
                closes = hours_info[day][f"{day}_hours_close"]
                hour_list.append(f"{day}: {opens}-{closes}")

            hours_of_operation = "; ".join(hour_list)

            store_number = store["properties"]["number"]

            latitude, longitude = (
                store["geometry"]["coordinates"][1],
                store["geometry"]["coordinates"][0],
            )
            if latitude == longitude:
                latitude = longitude = "<MISSING>"

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
