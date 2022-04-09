# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "gordonsjewelers.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "www.gordonsjewelers.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    base = "https://www.gordonsjewelers.com"
    search_url = "https://www.gordonsjewelers.com/store-finder/view-all-states"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    states = search_sel.xpath('//div[@class="inner-container" and .//h1]//div[./a]')

    for state in states:

        state_url = base + "/store-finder/" + "".join(state.xpath(".//@href"))

        log.info(state_url)
        if "/contact-us" in state_url:
            break
        state_res = session.get(state_url, headers=headers)
        state_sel = lxml.html.fromstring(state_res.text)

        store_list = state_sel.xpath(
            '//div[contains(@class,"view-all-stores")]//div[./div[@class="viewstoreslist"]]'
        )

        for store in store_list:

            if len("".join(store.xpath(".//a/@href"))) <= 0:
                continue
            page_url = base + "".join(store.xpath(".//a/@href"))

            locator_domain = website

            log.info(page_url)
            store_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)

            street_address = (
                " ".join(store.xpath('.//*[@itemprop="streetAddress"]//text()'))
                .strip()
                .strip("] ")
                .strip()
            )
            city = " ".join(
                store.xpath('.//*[@itemprop="addressLocality"]//text()')
            ).strip()
            state = " ".join(
                store.xpath('.//*[@itemprop="addressRegion"]//text()')
            ).strip()
            zip = " ".join(store.xpath('.//*[@itemprop="postalCode"]//text()')).strip()
            country_code = "US"

            location_name = "".join(store.xpath(".//a/text()")).strip()

            phone = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath('.//*[@itemprop="telephone"]/text()')
                    ],
                )
            )
            phone = phone[0].strip()

            store_number = page_url.split("-")[-1].upper()

            location_type = "<MISSING>"

            hours = json.loads(
                store_res.text.split("var storeInformation = ")[1]
                .strip()
                .split(";")[0]
                .strip()
                .replace("},", "}")
                .strip()
            )["openings"]
            hours_list = []
            for day in hours.keys():
                time = hours[day]
                hours_list.append(day + time)

            hours_of_operation = "; ".join(hours_list).strip()
            latitude, longitude = (
                "".join(store_sel.xpath('.//*[@itemprop="latitude"]//text()')).strip(),
                "".join(store_sel.xpath('.//*[@itemprop="longitude"]//text()')).strip(),
            )

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
