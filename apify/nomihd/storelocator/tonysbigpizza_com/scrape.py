# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "tonysbigpizza.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "tonysbigpizza.com",
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

    search_url = "https://tonysbigpizza.com/"

    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)

        stores = list(
            set(search_sel.xpath('//li/a[contains(text(),"Location Info")]/@href'))
        )

        for store_url in stores:

            page_url = store_url
            log.info(page_url)
            page_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(page_res.text)

            locator_domain = website

            location_name = (
                "".join(store_sel.xpath("//h2[@class='info-top-title']/text()"))
                .strip()
                .replace('"', "")
                .strip()
            )

            raw_address = "".join(
                store_sel.xpath('//p[@class="info-top-description"]/text()')
            ).strip()

            street_address = raw_address.split(",")[0].strip().rsplit(" ", 1)[0].strip()
            city = raw_address.split(",")[0].strip().rsplit(" ", 1)[-1].strip()
            state = raw_address.split(",")[-1].strip().split(" ")[0].strip()
            zip = raw_address.split(",")[-1].strip().split(" ")[-1].strip()
            country_code = "US"
            store_number = "<MISSING>"

            phone = "".join(
                store_sel.xpath('//a[@class="info-top-phone"]//text()')
            ).strip()

            location_type = "<MISSING>"

            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//div[@class="info-top-opening_hours"]//text()'
                        )
                    ],
                )
            )
            hours_of_operation = "; ".join(hours)
            latitude = "".join(store_sel.xpath('//div[@class="marker"]/@data-lat'))
            longitude = "".join(store_sel.xpath('//div[@class="marker"]/@data-lng'))

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
