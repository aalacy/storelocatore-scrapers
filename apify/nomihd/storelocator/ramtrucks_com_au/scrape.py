# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "ramtrucks.com.au"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.ramtrucks.com.au/locate-a-dealer/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)
        stores = search_sel.xpath('//div[@id="js-dealerResults"]/div')

        lat_list = search_res.text.split('"gmapLatitude":"')
        lng_list = search_res.text.split('"gmapLongitude":"')

        for index, store in enumerate(stores, 1):

            locator_domain = website

            location_name = "".join(
                store.xpath('.//p[@class="fdd-text fdd-text-name"]//text()')
            ).strip()

            store_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath(
                            './/div[contains(@class,"findDealerItemAddress")]//text()'
                        )
                    ],
                )
            )
            raw_address = "<MISSING>"

            street_address = " ".join(store_info[1:-3])

            city = store_info[-3].strip()

            state = store_info[-2].strip()
            zip = store_info[-1].strip()

            country_code = "AU"
            phone = "".join(store.xpath(".//a[contains(@href,'tel:')]//text()"))

            page_url = "https://www.ramtrucks.com.au" + "".join(
                store.xpath('.//a[contains(@href,"/locate-a-dealer")]/@href')
            )

            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            typ_list = []
            sales_addr = ", ".join(
                store_sel.xpath(
                    '//div[@data-id="ldidSales"]/div[@class="ldidItemWrapper"][./div[contains(text(),"Address:")]]/div[@class="ldidText"]/text()'
                )
            ).strip()

            service_addr = ", ".join(
                store_sel.xpath(
                    '//div[@data-id="ldidService"]/div[@class="ldidItemWrapper"][./div[contains(text(),"Address:")]]/div[@class="ldidText"]/text()'
                )
            ).strip()

            if len(sales_addr) > 0:
                typ_list.append("sales")
            else:
                sales_addr = service_addr  # when sales is missing

            if sales_addr == service_addr:
                typ_list.append("service")

            parts_addr = ", ".join(
                store_sel.xpath(
                    '//div[@data-id="ldidParts"]/div[@class="ldidItemWrapper"][./div[contains(text(),"Address:")]]/div[@class="ldidText"]/text()'
                )
            ).strip()

            if sales_addr == parts_addr:
                typ_list.append("parts")

            location_type = ", ".join(typ_list).strip()

            hours_of_operation = "; ".join(
                store_sel.xpath(
                    '//div[@data-id="ldidSales"]/div[./div[contains(text(),"Hours")]]/div[@class="ldidText"]/text()'
                )
            ).strip()
            if len(hours_of_operation) <= 0:
                hours_of_operation = "; ".join(
                    store_sel.xpath(
                        '//div[@data-id="ldidService"]/div[./div[contains(text(),"Hours")]]/div[@class="ldidText"]/text()'
                    )
                ).strip()

            if len(hours_of_operation) <= 0:
                hours_of_operation = "; ".join(
                    store_sel.xpath(
                        '//div[@data-id="ldidParts"]/div[./div[contains(text(),"Hours")]]/div[@class="ldidText"]/text()'
                    )
                ).strip()

            store_number = page_url.split("=")[1].strip()

            latitude, longitude = (
                lat_list[index].split('",')[0].strip(),
                lng_list[index].split('",')[0].strip(),
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
