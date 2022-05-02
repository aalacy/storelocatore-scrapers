# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "tenfour.co.jp"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.tenfour.co.jp",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "Referer": "https://www.tenfour.co.jp/store/store.php",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


data = {
    "area_type": "\u5317\u6D77\u9053",
    "store": "city",
}
store_data = {
    "store_cd": "00000126",
}


def fetch_data():
    # Your scraper here

    search_url = "https://www.tenfour.co.jp/store/store.php"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        log.info(search_res)

        search_sel = lxml.html.fromstring(search_res.text)

        areas = search_sel.xpath('//dl[@class="area"]//a')

        for no, _area in enumerate(areas, 1):

            locator_domain = website

            area_info = "".join(_area.xpath("./@onclick")).strip()
            area_type = (
                area_info.split(");")[0]
                .split("selectedArea(")[1]
                .split(",")[0]
                .strip("'")
                .strip()
            )

            data["area_type"] = area_type
            data["store"] = (
                area_info.split(");")[0]
                .split("selectedArea(")[1]
                .split(",")[1]
                .strip("'")
                .strip()
            )
            log.info(data)

            area_res = session.post(
                "https://www.tenfour.co.jp/store/store.php", headers=headers, data=data
            )
            log.info(area_res)
            area_sel = lxml.html.fromstring(area_res.text)

            stores = area_sel.xpath('//ul[@class="temposagasu"]/li/a')

            for n, store in enumerate(stores, 1):

                page_data = "".join(store.xpath("./@onclick"))
                store_data["store_cd"] = (
                    page_data.split("document.fm.store_cd.value=")[1]
                    .split(";")[0]
                    .strip("'")
                )
                page_url = "https://www.tenfour.co.jp/store/store_info.php"

                store_res = session.post(page_url, headers=headers, data=store_data)
                log.info(store_res)
                store_sel = lxml.html.fromstring(store_res.text)

                location_name = " ".join("".join(store.xpath(".//text()"))).strip()

                location_type = "<MISSING>"

                store_info = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store_sel.xpath(
                                '//dt[@class="address"]/following-sibling::dd[1]//text()'
                            )
                        ],
                    )
                )

                raw_address = ", ".join(store_info)

                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )

                if street_address is not None:
                    street_address = street_address.replace("Ste", "Suite")

                city = formatted_addr.city

                state = formatted_addr.state

                zip = formatted_addr.postcode

                country_code = "JP"

                phone = "".join(
                    store_sel.xpath(
                        '//dt[@class="tel"]/following-sibling::dd[1]//text()'
                    )
                )

                hours = list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store_sel.xpath(
                                '//dt[@class="eigyo"]/following-sibling::dd[1]//text()'
                            )
                        ],
                    )
                )
                if hours:

                    hours_of_operation = (
                        "; ".join(hours[:1])
                        .strip()
                        .replace("day; ", "day: ")
                        .replace("Show More", "")
                        .strip("; ")
                    )
                else:
                    hours_of_operation = "<MISSING>"

                store_number = store_data["store_cd"]

                latitude, longitude = "<MISSING>", "<MISSING>"

                page_url = "https://www.tenfour.co.jp/store/store.php"
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
