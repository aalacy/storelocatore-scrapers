# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "waynescoffee.com.sa"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.waynescoffee.com.sa/en/cafes/"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//ul[@id="map-items"]/li')
        for store in stores:
            page_url = "".join(store.xpath("a/@href")).strip()
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            locator_domain = website
            location_name = "".join(
                store.xpath(".//span[@class='store-name']/text()")
            ).strip()
            raw_address = "".join(
                store_sel.xpath("//div[@class='section-header'][./h1]/p/text()")
            ).strip()

            street_address = ", ".join(raw_address.split(",")[:-1]).strip()
            city = raw_address.split(",")[-1].strip()
            state = "<MISSING>"
            zip = "".join(
                store_sel.xpath(
                    '//div[@class="cafe-information-row"][./h2[contains(text(),"Address")]]/p[1]/text()'
                )
            ).strip()

            if len(zip) > 0:
                zip = (
                    zip.replace("\t\t\t\t\t\t\t\t", " ").strip().rsplit(" ")[-2].strip()
                )
            else:
                zip = "<MISSING>"

            country_code = "SA"

            store_number = "<MISSING>"
            phone = "".join(store_sel.xpath('//a[@class="link_phone"]/text()')).strip()

            location_type = "<MISSING>"
            hours = store_sel.xpath("//ul[@class='cafe-opening-hours-list']/li")
            hours_list = []
            for hour in hours:
                day = "".join(hour.xpath("text()")).strip()
                time = "".join(hour.xpath("span/text()")).strip()
                hours_list.append(day + ":" + time)

            hours_of_operation = "; ".join(hours_list).strip()

            map_link = "".join(store_sel.xpath('//div[@id="cafe_map"]/@rel')).strip()
            latitude, longitude = (
                map_link.split(",")[0].strip(),
                map_link.split(",")[-1].strip(),
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
