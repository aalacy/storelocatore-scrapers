# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "shoecity.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "shoecity.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://shoecity.com/pages/shoe-city-locations"
    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        all_store_info = search_sel.xpath("//tr/td//text()")
        all_store_info = (" | ".join(all_store_info)).split(" |   |   |   | ")

        for info in all_store_info[:]:

            page_url = search_url

            locator_domain = website

            no_of_stores = info.count("Shoe City")

            if no_of_stores > 0:
                cleaned_info = list(filter(str, [x.strip() for x in info.split("|")]))

                for no in range(no_of_stores):  # normally 3

                    target_index = no
                    location_name = cleaned_info[target_index]

                    target_index += no_of_stores
                    street_address = cleaned_info[target_index]

                    target_index += no_of_stores
                    city_state_zip = cleaned_info[target_index].split(",")
                    city = city_state_zip[0].strip()
                    state = city_state_zip[1].strip().split(" ")[0].strip()
                    zip = city_state_zip[1].strip().split(" ")[1].strip()
                    country_code = "US"

                    target_index += no_of_stores
                    phone = cleaned_info[target_index].strip()
                    store_number = "<MISSING>"

                    location_type = "<MISSING>"

                    hours_of_operation = "<MISSING>"
                    latitude, longitude = "<MISSING>", "<MISSING>"

                    raw_address = "<MISSING>"
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
