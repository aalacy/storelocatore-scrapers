# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "pizzahut.cw"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "pizzahut.cw",
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
    search_url = "https://pizzahut.cw/opening-hours"
    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        section_list = search_sel.xpath("//table//tr[.//h2]")

        for idx, section in enumerate(section_list, 1):
            store_list = section.xpath(".//h2")
            for x, store in enumerate(store_list, 1):
                undesired_store = section.xpath("./following-sibling::tr//h2//text()")
                if undesired_store:
                    undesired_store = undesired_store[x - 1]
                raw_info = section.xpath(f"./following-sibling::tr/td[{x}]//text()")

                if undesired_store:
                    for spliter, info in enumerate(raw_info):
                        if undesired_store in info:
                            store_info = raw_info[:spliter]
                else:
                    store_info = raw_info

                store_info = list(filter(str, [_info.strip() for _info in store_info]))

                page_url = search_url
                location_name = "".join(store.xpath(".//text()")).strip()
                locator_domain = website

                street_address = store_info[0].strip()
                city = "<MISSING>"
                state = location_name
                zip = "<MISSING>"

                country_code = "CW"

                phone = store_info[1].strip()
                store_number = "<MISSING>"

                location_type = "<MISSING>"
                if "+59" in store_info[2]:

                    hours_of_operation = "; ".join(store_info[3:]).strip()
                else:
                    hours_of_operation = "; ".join(store_info[2:]).strip()
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
