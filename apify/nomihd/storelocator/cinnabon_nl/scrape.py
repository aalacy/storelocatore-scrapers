# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "cinnabon.nl"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "cinnabon.nl",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://cinnabon.nl/vestigingen/"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = search_sel.xpath(
        '//div[./div[1]/div/div/a[contains(text(),"Navigeer naar locatie")]]'
    )

    for store in store_list:

        page_url = search_url

        locator_domain = website
        location_name = "".join(
            store.xpath('.//h2[@class="et_pb_module_header"]/text()')
        ).strip()

        raw_address = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store.xpath(
                        ".//div[@class='et_pb_promo_description']/div/p[3]/text()"
                    )
                ],
            )
        )

        phone = "".join(
            store.xpath(
                ".//div[@class='et_pb_promo_description']/div/p/a[contains(@href,'tel:')]/text()"
            )
        )
        street_address = raw_address[0].strip()
        city = raw_address[1].strip().split(" ")[-1]
        state = raw_address[1].strip().split(" ")[-2]
        zip = raw_address[1].strip().split(" ")[0]
        country_code = "NL"

        store_number = "<MISSING>"

        location_type = "<MISSING>"
        hours = store.xpath(".//table//tr")
        hours_list = []
        for hour in hours:
            day = "".join(hour.xpath("td[1]/text()")).strip()
            time = "".join(hour.xpath("td[2]//text()")).strip()
            hours_list.append(day + ": " + time)

        hours_of_operation = "; ".join(hours_list).strip()
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
