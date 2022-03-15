# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgpostal import sgpostal as parser
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "168markets.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "http://168markets.com/index.html"
    search_req = session.get(search_url, headers=headers)
    search_sel = lxml.html.fromstring(search_req.text)
    locations = search_sel.xpath('//li[@id="locations"]/ul/li/a/@href')
    for loc_url in locations:

        page_url = "http://168markets.com/" + loc_url
        log.info(page_url)
        stores_req = session.get(page_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath(
            '//td/div[@class="wrapper"]/div[@class="grid_5 suffix_1"]/table'
        )
        if len(stores) <= 0:
            stores = stores_sel.xpath(
                '//div[@class="wrapper"]/div[@class="grid_5 suffix_1"]/table'
            )
        for store in stores:
            locator_domain = website

            location_name = "".join(store.xpath(".//tr/td[3]/h4/text()")).strip()
            if len(location_name) <= 0:
                continue
            add_sections = store.xpath(".//tr/td[3]//p")
            add_list = []
            for add in add_sections:
                if len("".join(add.xpath(".//text()")).strip()) > 0:
                    add_list.append("".join(add.xpath(".//text()")).strip())

            raw_address = ", ".join(add_list[:2]).strip().replace(",,", ",").strip()
            formatted_addr = parser.parse_address_usa(raw_address)
            street_address = formatted_addr.street_address_1
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2

            city = formatted_addr.city
            state = formatted_addr.state
            zip = formatted_addr.postcode

            country_code = "US"

            store_number = "<MISSING>"

            phone = "".join(
                store.xpath(
                    './/tr/td[3]/dl/dd/strong[contains(text(),"Telephone:")]/span/text()'
                )
            ).strip()

            location_type = "<MISSING>"
            hours_of_operation = "<MISSING>"
            try:
                hours_of_operation = (
                    "; ".join(add_list[3:])
                    .strip()
                    .replace("Office Hours:", "")
                    .strip()
                    .replace("BUSINESS HOURS:;", "")
                    .strip()
                )
            except:
                pass
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            map_link = "".join(
                store.xpath('.//a[contains(@onclick,"google.com/maps")]/@onclick')
            ).strip()

            if len(map_link) > 0 and "/@" in map_link:
                latitude = map_link.split("/@")[1].strip().split(",")[0].strip()
                longitude = map_link.split("/@")[1].strip().split(",")[1]

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
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
