# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "ewm.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.ewm.co.uk/store-finder/"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        stores_req = session.get(search_url, headers=headers)
        stores_json = json.loads(
            stores_req.text.split("storelocator.sources = ")[1]
            .strip()
            .split("}}];")[0]
            .strip()
            + "}}]"
        )

        cord_dict = {}
        for data in stores_json:
            cord_dict[data["id"]] = data["lat"] + "," + data["lng"]

        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath(
            '//div[@id="storelocator_scroll"]/div[@class="source GB"]'
        )

        for store in stores:
            store_number = "".join(
                store.xpath('div[@class="go-to-source"]/@id')
            ).strip()
            page_url = (
                "https://www.ewm.co.uk/storelocator/store/index?source_code="
                + store_number
            )

            locator_domain = website
            location_name = "".join(
                store.xpath('div[@class="go-to-source"]/text()')
            ).strip()

            address = "".join(
                store.xpath(
                    './/div[@class="store-info container"]/div[1]/div[1]/p[1]/text()'
                )
            ).strip()

            city = ""
            if "," in location_name:
                city = location_name.split(",")[-1].strip()

            street_address = ""
            add_list = []
            try:
                temp_addr = address.split(",")
                for add in temp_addr:
                    if len("".join(add).strip()) > 0:
                        if add.strip() == city:
                            break
                        else:
                            add_list.append("".join(add).strip())

            except:
                pass

            street_address = ", ".join(add_list).strip()
            if len(street_address) <= 0:
                street_address = "Colliers Street"
            state = "<MISSING>"
            zip = address.split(",")[-2].strip()
            country_code = "GB"

            phone = "".join(
                store.xpath(
                    './/div[@class="store-info container"]/div[1]/div[1]/p[2]/text()'
                )
            ).strip()

            location_type = "<MISSING>"

            latitude = ""
            longitude = ""

            if store_number in cord_dict:
                latlng = cord_dict[store_number]
                latitude = latlng.split(",")[0].strip()
                longitude = latlng.split(",")[1].strip()

            hours_of_operation = ""
            hours = store.xpath(
                './/div[@class="store-info container"]/div[1]/div[2]/p/text()'
            )
            hours_list = []
            for hour in hours:
                if len("".join(hour).strip()) > 0:
                    hours_list.append("".join(hour).strip())

            hours_of_operation = "; ".join(hours_list).strip()

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
