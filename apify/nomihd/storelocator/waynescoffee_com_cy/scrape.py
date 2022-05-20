# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "waynescoffee.com.cy"
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
    search_url = "https://www.waynescoffee.com.cy/cafes/"
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
                store_sel.xpath("//h1[@class='single-cafe__title']/span[1]/text()")
            ).strip()
            raw_address = list(
                filter(
                    str,
                    store_sel.xpath(
                        '//div[@class="single-cafe__content"][./p/strong[contains(text(),"Address")]]/p/text()'
                    ),
                )
            )

            street_address = raw_address[0]
            city = raw_address[-1].split(" ", 1)[-1].strip()
            state = "<MISSING>"
            zip = raw_address[-1].split(" ", 1)[0].strip()

            country_code = "CY"

            store_number = "".join(
                store_sel.xpath('//ul[@id="cafe-opening-hours-list"]/@data-storeid')
            ).strip()
            phone = (
                "".join(store_sel.xpath('//a[@class="link_phone"]/text()'))
                .strip()
                .replace("Contact:", "")
                .strip()
            )

            location_type = "<MISSING>"
            hours_req = session.get(
                f"https://www.waynescoffee.jo/theme/ajax.php?action=cafe_opening&storeid={store_number}",
                headers=headers,
            )
            hours_sel = lxml.html.fromstring(hours_req.json()["data"])
            hours = hours_sel.xpath("//li")
            hours_list = []
            for hour in hours:
                day = "".join(
                    hour.xpath('.//span[@class="opening-hours__day"]/text()')
                ).strip()
                time = "".join(
                    hour.xpath('.//span[@class="opening-hours__time"]/text()')
                ).strip()
                if not time:
                    time = "".join(hour.xpath("p[2]/text()")).strip()

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
                raw_address=", ".join(raw_address).strip(),
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
