# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html
from sgpostal import sgpostal as parser

website = "adairs.com.au"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.adairs.com.au",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.adairs.com.au/stores/"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        json_data = json.loads(
            stores_req.text.split("window.adairs.stores= '")[1]
            .strip()
            .split("';</script>")[0]
            .strip()
            .replace("&quot;", '"')
            .strip()
        )

        loc_types = json_data["StoreCategoryFilters"]
        type_dict = {}
        for loc in loc_types:
            type_dict[loc["StoreCategoryId"]] = loc["StoreCategoryName"]

        stores = json_data["Stores"]
        for store in stores:
            store_number = "<MISSING>"
            page_url = "https://www.adairs.com.au" + store["StorePageUrl"]
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            locator_domain = website
            location_name = store["StoreName"]

            raw_address = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//div[@class="store__location row"]/div[contains(@class,"address")]/p[not(./a)]/text()'
                        )
                    ],
                )
            )

            city = raw_address[-1].strip().split(",")[0].strip()
            if not city:
                city = location_name

            state = store["StoreState"]
            zip = raw_address[-1].strip().rsplit(" ", 1)[-1].strip()
            country_code = "AU"
            phone = store.get("StorePhone", "<MISSING>")

            type_list = []
            cat_list = store["StoreCate"]
            for c in cat_list:
                if c in type_dict.keys():
                    type_list.append(type_dict[c])

            location_type = ", ".join(type_list).strip()

            latitude = store["Location"]["Lat"]
            longitude = store["Location"]["Lng"]

            hours_of_operation = "<MISSING>"
            hours = store_sel.xpath('//div[@class="store__info row"]//table//tr[td]')
            hours_list = []
            for hour in hours:
                day = "".join(hour.xpath("td[1]/text()")).strip()
                time = "".join(hour.xpath("td[2]/text()")).strip()
                hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()

            raw_address = ", ".join(raw_address).strip()

            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

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
