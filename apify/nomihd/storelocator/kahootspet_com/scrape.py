# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "kahootspet.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "kahootsfeedandpet.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://kahootsfeedandpet.com/pages/locations"
    stores_req = session.get(search_url, headers=headers)
    stores_sel = lxml.html.fromstring(stores_req.text)
    stores = stores_sel.xpath('//div[contains(@class,"location-card")]')
    for store in stores:
        page_url = (
            "https://kahootsfeedandpet.com"
            + "".join(store.xpath("div/a/@href")).strip()
        )
        locator_domain = website
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        location_name = "".join(
            store_sel.xpath('//div[contains(@class,"hero-main")]/div/h1/text()')
        ).strip()

        address = store_sel.xpath(
            '//div[@class="mid"]/div[contains(@class,"right")]/p[2]/text()'
        )
        add_list = []
        for add in address:
            if len("".join(add).strip()) > 0:
                add_list.append("".join(add).strip())

        street_address = add_list[0].strip()
        city = add_list[1].split(",")[0].strip()
        state = add_list[1].split(",")[1].strip().split(" ")[0].strip()
        zip = add_list[1].split(",")[1].strip().split(" ")[-1].strip()

        country_code = "US"

        store_number = "<MISSING>"
        phone = "".join(
            store_sel.xpath(
                '//div[@class="mid"]/div[contains(@class,"right")]/p/a[contains(@href,"tel:")]/text()'
            )
        ).strip()

        location_type = "".join(store.xpath("@data-storetype")).strip()
        hours = store_sel.xpath(
            '//div[@class="mid"]/div[contains(@class,"left")]/p[position()<=2]'
        )
        hours_list = []
        for hour in hours:
            day = "".join(hour.xpath("strong/text()")).strip()
            if len(day) > 0:
                time = "".join(hour.xpath("text()")).strip()
                hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()

        latitude = store_req.text.split('{"lat":')[1].strip().split(",")[0].strip()
        longitude = store_req.text.split('"lng":')[1].strip().split("}")[0].strip()

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
