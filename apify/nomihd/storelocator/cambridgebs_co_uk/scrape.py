# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "cambridgebs.co.uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.cambridgebs.co.uk/contact",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.cambridgebs.co.uk/Umbraco/Api/ConsumerBranch/Branchs"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores = json.loads(stores_req.text)["branchList"]
        for store in stores:
            page_url = "https://www.cambridgebs.co.uk" + store["Link"]
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            locator_domain = website
            location_name = store["BranchName"]
            if "Opening Soon" in location_name:
                continue
            addr_sel = lxml.html.fromstring(store["BranchAddress"])
            temp_add = addr_sel.xpath(".//text()")
            add_list = []
            for temp in temp_add:
                if (
                    len("".join(temp).strip()) > 0
                    and "Head Office" not in temp
                    and "Speak to" not in temp
                ):
                    add_list.append("".join(temp).strip())

            if len(add_list) > 1:
                street_address = ", ".join(add_list[:-1]).strip()
                city = add_list[-1].strip()
            else:
                street_address = "".join(add_list).strip().split(",")[0].strip()
                city = "".join(add_list).strip().split(",")[-1].strip()

            if street_address[-1] == ",":
                street_address = "".join(street_address[:-1]).strip()

            state = "<MISSING>"
            zip = store["PostCode"]
            country_code = "GB"
            phone = store["BranchTelephone"]
            location_type = "<MISSING>"
            store_number = store["BranchId"]
            hours = store_sel.xpath('//div[@class="day-instance"]')
            hours_list = []
            for hour in hours:
                day = "".join(hour.xpath("span[1]/text()")).strip()
                if "Bank Holiday" == day:
                    continue
                time = "".join(hour.xpath("span[2]/text()")).strip()
                hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()

            latitude = store["Latitude"]
            longitude = store["Longitude"]
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
