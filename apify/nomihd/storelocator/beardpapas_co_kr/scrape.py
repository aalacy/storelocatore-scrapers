# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser

website = "beardpapas.co.kr"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "http://beardpapas.co.kr/bbs/board.php?bo_table=store"
    url_list = []
    with SgRequests() as session:
        while True:
            stores_req = session.get(search_url, headers=headers)
            stores_sel = lxml.html.fromstring(stores_req.text)
            stores = stores_sel.xpath('//div[@class="maplist"]/ul')
            latlng_list = stores_req.text.split("latlng: new daum.maps.LatLng(")
            for index in range(0, len(stores)):
                page_url = search_url
                locator_domain = website

                store_number = "<MISSING>"

                location_type = "<MISSING>"

                location_name = "".join(
                    stores[index].xpath('li[@class="t"]/text()')
                ).strip()

                raw_address = "".join(
                    stores[index].xpath('li[@class="data-link"]/text()')
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

                phone = "".join(
                    stores[index].xpath(
                        'div[@class="r"]/ul/li[./i[@class="fa fa-phone"]]/text()'
                    )
                ).strip()

                hours_of_operation = "".join(
                    stores[index].xpath(
                        'div[@class="r"]/ul/li[./i[@class="fa fa-clock-o"]]/text()'
                    )
                ).strip()

                latitude, longitude = (
                    latlng_list[index + 1].split(",")[0].strip(),
                    latlng_list[index + 1].split(",")[1].strip().split(")")[0].strip(),
                )

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

            next_page = "".join(
                stores_sel.xpath('.//a[@class="pg_page"]/@href')
            ).strip()
            if next_page in url_list:
                break
            else:
                url_list.append(next_page)
                search_url = (
                    "http://beardpapas.co.kr/bbs" + next_page.replace("./", "/").strip()
                )
                log.info(search_url)


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
