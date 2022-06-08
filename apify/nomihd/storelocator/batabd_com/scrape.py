# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "batabd.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.batabd.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "cross-site",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.batabd.com/pages/bata-stores"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//div[@class="rte"]/table//tr[position()>1]')
        for store in stores:

            store_number = "<MISSING>"
            page_url = search_url
            locator_domain = website

            location_name = "".join(store.xpath("td[2]/text()")).strip()
            if len(location_name) <= 0:
                continue
            street_address = (
                "".join(store.xpath("td[3]/text()")).strip().rsplit(",", 1)[0].strip()
            )
            city = "".join(store.xpath("td[1]/text()")).strip()
            state = "<MISSING>"
            zip = "<MISSING>"
            country_code = "BD"
            phone = "".join(store.xpath("td[4]/text()")).strip()

            location_type = "<MISSING>"
            hours = stores_sel.xpath('//div[@class="rte"]/h3/span/text()')
            hours_list = []
            for hour in hours:
                hours_list.append("".join(hour).strip().split(":")[-1].strip())

            hours_of_operation = " - ".join(hours_list).strip()

            latitude, longitude = "<MISSING>", "<MISSING>"

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
        deduper=SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.PHONE})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
