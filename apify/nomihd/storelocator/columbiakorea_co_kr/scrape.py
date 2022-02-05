# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html
from sgpostal import sgpostal as parser

website = "columbiakorea.co.kr"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.columbiakorea.co.kr",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "referer": "https://www.columbiakorea.co.kr/about/store.asp",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here

    with SgRequests(dont_retry_status_codes=([404])) as session:
        loc_req = session.get(
            "https://www.columbiakorea.co.kr/about/store.asp", headers=headers
        )
        loc_sel = lxml.html.fromstring(loc_req.text)
        loc_types = loc_sel.xpath('//select[@name="stType_s"]/option[position()>1]')
        for typ in loc_types:
            search_url = "https://www.columbiakorea.co.kr/about/store.asp?stKeyword=&stBrand=CO&stLocal=&stType={}"
            location_type = "".join(typ.xpath("text()")).strip()
            loc_val = "".join(typ.xpath("@value")).strip()
            while True:
                log.info(search_url)
                search_res = session.get(search_url.format(loc_val), headers=headers)
                search_sel = lxml.html.fromstring(search_res.text)
                stores = search_sel.xpath('//tr[@class="list__basic__info"]')

                for store in stores:

                    page_url = search_url

                    locator_domain = website

                    location_name = "".join(store.xpath("td[2]/text()")).strip()

                    raw_address = "".join(
                        store.xpath('td[@class="address"]/text()')
                    ).strip()
                    formatted_addr = parser.parse_address_intl(raw_address)
                    street_address = formatted_addr.street_address_1
                    if formatted_addr.street_address_2:
                        street_address = (
                            street_address + ", " + formatted_addr.street_address_2
                        )

                    city = formatted_addr.city
                    state = formatted_addr.state
                    zip = formatted_addr.postcode

                    country_code = "KR"

                    store_number = "".join(
                        store.xpath(".//a[@data-no]/@data-no")
                    ).strip()
                    phone = "".join(store.xpath("td[4]/text()")).strip()
                    hours_of_operation = "<MISSING>"

                    latitude, longitude = "<MISSING>", "<MISSING>"

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

                next_page = search_sel.xpath('//a[@class="paging__next"]/@href')
                if len(next_page) > 0:
                    if "javascript" in next_page[0]:
                        break
                    else:
                        search_url = (
                            "https://www.columbiakorea.co.kr/about/store.asp"
                            + next_page[0]
                        )
                else:
                    break


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
