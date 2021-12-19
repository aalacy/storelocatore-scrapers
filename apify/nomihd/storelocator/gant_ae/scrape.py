# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "gant.ae"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    base = "https://www.gant.ae"
    search_url = "https://www.gant.ae/map"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)
        stores = search_sel.xpath('//div[@class="store-locator__stores"]/div/div')

        for no, store in enumerate(stores, 1):

            locator_domain = website

            location_name = "".join(
                store.xpath('.//*[@itemprop="name"]//text()')
            ).strip()

            location_type = "<MISSING>"

            store_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath(
                            './/*[@class="row store-locator__store__info"]//p//text()'
                        )
                    ],
                )
            )
            raw_address = "<MISSING>"

            street_address = " ".join(store_info[:-2]).strip()

            city = store_info[-2].strip()
            state = "<MISSING>"
            zip = "<MISSING>"
            country_code = "AE"

            phone = "".join(store.xpath('.//a[contains(@href,"tel:")]/text()'))
            page_url = (
                base + "".join(store.xpath('.//*[@itemprop="name"]/../@href')).strip()
            )

            hours_of_operation = "<MISSING>"

            store_number = page_url.split("/")[-1].strip()
            map_info = search_res.text.split(
                f"var m{no}_marker_latlng=new google.maps.LatLng("
            )[1].split(")")[0]
            latitude, longitude = map_info.split(",")[0], map_info.split(",")[1]

            if len(latitude) <= 0:
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                map_info = store_req.text.split("myLatlng=new google.maps.LatLng(")[
                    1
                ].split(")")[0]
                latitude, longitude = map_info.split(",")[0], map_info.split(",")[1]
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
