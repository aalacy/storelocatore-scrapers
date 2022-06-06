# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "2ndandcharles.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    # Your scraper here
    search_url = "https://2ndandcharles.com/locations"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//div[@class="w-dyn-item"]/a/@href')
        for store_url in stores:
            page_url = "https://2ndandcharles.com" + store_url
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            locator_domain = website
            location_name = "".join(
                store_sel.xpath('//h1[@class="store-head"]/text()')
            ).strip()
            street_address = "".join(
                store_sel.xpath('//div[@class="store-info"]/div[1]/text()')
            ).strip()

            city_state_zip = (
                "".join(store_sel.xpath('//div[@class="card-citystate"]/div/text()'))
                .strip()
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "")
                .strip()
            )
            city = city_state_zip.split(",")[0].strip()
            if not location_name:
                location_name = city

            state = city_state_zip.split(",")[1]
            zip = city_state_zip.split(",")[2]

            country_code = "US"
            store_number = "<MISSING>"
            phone = "".join(
                store_sel.xpath('//div[@class="store-info"]/div[3]/text()')
            ).strip()
            if not phone:
                phone = "".join(
                    store_sel.xpath(
                        '//div[@class="store-info"]/a[@class="phone"]/text()'
                    )
                ).strip()

            location_type = "<MISSING>"
            days = store_sel.xpath('//div[@class="hours"][1]/div')
            time = store_sel.xpath('//div[@class="hours"][2]/div')
            hours_list = []
            for index in range(0, len(days)):
                hours_list.append(
                    "".join(days[index].xpath("text()")).strip()
                    + ":"
                    + "".join(time[index].xpath("text()")).strip()
                )

            hours_of_operation = "; ".join(hours_list).strip()

            map_link = "".join(
                store_sel.xpath('//a[contains(text(),"Get Directions")]/@href')
            ).strip()
            latitude = ""
            longitude = ""
            if len(map_link) > 0:
                if "sll=" in map_link:
                    latitude = map_link.split("sll=")[1].strip().split(",")[0].strip()
                    longitude = (
                        map_link.split("sll=")[1]
                        .strip()
                        .split(",")[1]
                        .strip()
                        .split("&")[0]
                        .strip()
                    )
                elif "/@" in map_link:
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
