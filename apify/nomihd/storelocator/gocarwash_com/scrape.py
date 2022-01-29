# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "gocarwash.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://gocarwash.com/locations/"
    api_url = "https://gocarwash.com/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMo5R0gEJFGeUFni6FAPFomOBAsmlxSX5uW6ZqTkpELFapVoABaMWvA"

    with SgRequests() as session:
        api_res = session.get(api_url, headers=headers)
        json_res = json.loads(api_res.text)

        stores = json_res["markers"]

        for idx, store in enumerate(stores, 1):

            locator_domain = website

            location_name = store["title"].strip()
            page_url = (
                search_url
                + location_name.lower().replace(" ", "-").replace(".", "").strip()
                + "/"
            )
            if "Coming Soon" in store["description"]:
                continue

            location_type = "<MISSING>"
            log.info(page_url)
            store_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)

            phone = store_sel.xpath('//a[contains(@href,"tel:")]//text()')
            if phone:
                phone = phone[0].strip()
            else:
                phone = "<MISSING>"
            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath('//div[@class="timing"]//text()')
                    ],
                )
            )
            if hours:
                hours_of_operation = "; ".join(hours)
            else:
                hours_of_operation = "<MISSING>"

            raw_address = store["address"]
            formatted_addr = parser.parse_address_usa(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            if street_address is not None:
                street_address = street_address.replace("Ste", "Suite")
            city = formatted_addr.city
            state = formatted_addr.state
            if state:
                state = state.replace(", Usa", "").strip()

            zip = formatted_addr.postcode
            if not zip:
                temp_address = "".join(
                    store_sel.xpath('//div[@class="address"]/p/text()')
                ).strip()
                zip = temp_address.split(",")[-1].strip().split(" ")[-1].strip()
            country_code = "US"

            store_number = store["id"]

            latitude, longitude = store["lat"], store["lng"]

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
