# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "fiat.ru"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.fiat-professional.ru",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "accept": "*/*",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://www.fiat-professional.ru",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "http://www.fiat.ru/dealers"
    api_url = "https://www.fiat-professional.ru/new-fiat/dealers-fiat-ru/"

    with SgRequests() as session:
        api_res = session.get(api_url, headers=headers)
        json_str = (
            api_res.text.split("var dealerList =")[1].split("</script>")[0].strip()
        )
        json_res = json.loads(json_str)
        stores = json_res

        for store in stores:

            locator_domain = website

            location_name = store["dealer_name_en"]
            page_url = search_url

            location_type = "<MISSING>"

            raw_address = store["dealer_adress_en"]

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")
            city = formatted_addr.city
            state = store["dealer_region_name_en"]
            zip = formatted_addr.postcode

            country_code = "RU"

            if store["dealer_phone"]:

                phone = store["dealer_phone"][0]
            elif store["dealer_sc_phone"]:

                phone = store["dealer_sc_phone"][0]
            else:
                phone = "<MISSING>"
            hours_of_operation = "<MISSING>"

            store_number = store["id"]

            latitude, longitude = store["dealer_latitude"], store["dealer_longitude"]

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
