# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "clarksmarket.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.clarksmarket.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.clarksmarket.com/"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)

        stores = stores_sel.xpath(
            '//a[contains(@href,"/locations/") and contains(@id,"main-")]/@href'
        )
        for store_url in stores:
            page_url = "https://clarksmarket.com" + store_url
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            locator_domain = website
            location_name = "".join(
                store_sel.xpath("//div[@class='store-location']/h1/text()")
            ).strip()

            temp_address = store_sel.xpath(
                "//div[@class='store-location']//h3[contains(text(),'Address')]/following-sibling::p/text()"
            )
            add_list = []
            for temp in temp_address:
                if len("".join(temp).strip()) > 0:
                    add_list.append("".join(temp).strip())

            street_address = add_list[0].strip()
            city = add_list[-1].strip().split(",")[0].strip()
            state = add_list[-1].strip().split(",")[-1].strip().split(" ", 1)[0].strip()
            zip = add_list[-1].strip().split(",")[-1].strip().split(" ", 1)[-1].strip()
            country_code = "US"

            phone = "".join(
                store_sel.xpath(
                    "//div[@class='store-location']//h3[text()='Phone Number']/following-sibling::a[1]/text()"
                )
            ).strip()
            location_type = "<MISSING>"

            hours = store_sel.xpath(
                "//div[@class='store-location']//h3[contains(text(),'Store Hours')]/following-sibling::div[1]/p"
            )
            hours_list = []
            for hour in hours:
                if len("".join(hour.xpath(".//text()")).strip()) > 0:
                    hours_list.append("".join(hour.xpath(".//text()")).strip())

            hours_of_operation = "; ".join(hours_list).strip()

            store_number = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"

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
