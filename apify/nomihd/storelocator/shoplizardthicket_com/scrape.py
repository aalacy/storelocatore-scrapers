# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "shoplizardthicket.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.shoplizardthicket.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.shoplizardthicket.com/storelocator/"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = search_sel.xpath('//a[@class="view-detail"]/@href')

    for store_url in store_list:

        page_url = store_url
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text)

        locator_domain = website
        location_name = "".join(
            store_sel.xpath('//div[@class="store-info"]/h4/text()')
        ).strip()

        full_address = (
            "".join(
                store_sel.xpath(
                    '//div[@class="store-info"]/p[@class="address-store"]/text()'
                )
            )
            .strip()
            .split(",")
        )

        street_address = (
            ", ".join(full_address[:-3]).strip().replace(",  Alpharetta", "").strip()
        )
        city = location_name.split(",")[0].strip()
        if street_address == "378 Newnan Crossing Bypass Newnan":
            street_address = "378 Newnan Crossing Bypass"

        state = full_address[-2].strip()
        zip = full_address[-1].split("-")[-1].strip()
        country_code = "US"

        store_number = "<MISSING>"

        location_type = "<MISSING>"
        phone = "<MISSING>"
        try:
            phone = (
                store_req.text.split("Phone no:</strong></td><td><p>")[1]
                .strip()
                .split("</")[0]
                .strip()
            )
        except:
            pass

        hours = store_sel.xpath('//table[@class="table"]//tr')
        hours_list = []
        for hour in hours:
            day = "".join(hour.xpath("td[1]/text()")).strip()
            time = "".join(hour.xpath("td[2]/text()")).strip()
            hours_list.append(day + time)

        hours_of_operation = "; ".join(hours_list).strip()
        latitude = store_req.text.split("lat:")[1].strip().split(",")[0].strip()
        longitude = store_req.text.split("lng:")[1].strip().split(",")[0].strip()

        raw_address = "<MISSING>"

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
