# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "patsselect.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.patsselect.com/locations"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath(
            '//div[@class="row js-group-row"][.//p[@class="fp-el"]//a]//p[@class="fp-el"]//a'
        )
        stores_info_list = stores_sel.xpath(
            '//div[@class="fp-el js-cb-text js-cb-element ai-dotted-wrap js-aieditor-title js-paragraph js-p-elediv js-item"][./p[@class="fp-el" and @style="text-align: center;"]/text()]'
        )
        for index in range(0, len(stores)):
            page_url = "https:" + "".join(stores[index].xpath("@href")).strip()

            locator_domain = website
            location_name = "".join(stores[index].xpath(".//text()")).strip()

            raw_address = stores_info_list[index].xpath(
                'p[@class="fp-el" and @style="text-align: center;"]/text()'
            )

            street_address = raw_address[0].strip()
            if "," == street_address[-1]:
                street_address = "".join(street_address[:-1]).strip()
            city = raw_address[1].strip().split(",")[0].strip()
            state_zip = raw_address[1].strip().split(",")[-1].strip()
            state = state_zip.split(" ")[0].strip()
            zip = state_zip.split(" ")[-1].strip()

            country_code = "US"

            store_number = "<MISSING>"
            phone = raw_address[-1].strip()

            location_type = "<MISSING>"

            hours_of_operation = "<MISSING>"

            latitude = "<MISSING>"
            longitude = "<MISSING>"

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
