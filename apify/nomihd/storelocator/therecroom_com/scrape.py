# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "therecroom.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.therecroom.com",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}


def fetch_data():
    # Your scraper here
    base = "https://www.therecroom.com"
    search_url = "https://www.therecroom.com/Home/BootstrapDialog"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        store_list = list(search_sel.xpath('//div[@class="row"]/div[.//a]'))

        for store in store_list:

            page_url = (
                base
                + "".join(store.xpath(".//a/@href"))
                .strip()
                .replace("Home/SetCookie?location=", "")
                .strip()
                + "/info"
            )
            locator_domain = website
            log.info(page_url)
            store_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)

            location_name = "".join(store.xpath(".//h2//text()"))

            store_info = list(
                filter(
                    str,
                    [x.strip() for x in store.xpath("./div[1]//text()")],
                )
            )

            full_address = store_info[1:]

            street_address = full_address[0]
            city = full_address[1].split(",")[0]
            state = full_address[1].split(",")[1]
            zip = full_address[2].strip()
            country_code = "CA"
            store_number = "<MISSING>"

            phone = "".join(
                list(
                    filter(
                        str,
                        [
                            x.strip()
                            for x in store_sel.xpath(
                                '//a[contains(@href,"tel:")]/text()'
                            )
                        ],
                    )
                )
            ).strip()

            location_type = "<MISSING>"

            hours = store_sel.xpath('//table[@class="hours"]//tr[./td]')
            hours_list = []
            for hour in hours:
                day = "".join(hour.xpath('td[@class="date"]/text()')).strip()
                time = "".join(hour.xpath('td[@class="time"]/text()')).strip()
                hours_list.append(day + time)

            hours_of_operation = "; ".join(hours_list).strip()

            latitude, longitude = "<MISSING>", "<MISSING>"

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
