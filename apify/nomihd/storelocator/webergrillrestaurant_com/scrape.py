# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html


website = "webergrillrestaurant.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "webergrillrestaurant.com",
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
    search_url = "https://webergrillrestaurant.com/"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = list(
        set(search_sel.xpath('//div[contains(@id,"locations-bar")]//a/@href'))
    )

    for store in store_list:

        page_url = store
        locator_domain = website
        log.info(page_url)
        store_res = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_res.text)

        location_name = "".join(store_sel.xpath("//title/text()"))

        street_address = " ".join(
            list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//*[@itemprop="streetAddress"]//text()'
                        )
                    ],
                )
            )
        ).strip()

        city = "".join(
            list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//*[@itemprop="addressLocality"]//text()'
                        )
                    ],
                )
            )
        ).strip()
        state = "".join(
            list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//*[@itemprop="addressRegion"]//text()'
                        )
                    ],
                )
            )
        ).strip()
        zip = "".join(
            list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath('//*[@itemprop="postalCode"]//text()')
                    ],
                )
            )
        ).strip()
        country_code = "US"

        store_number = "<MISSING>"
        phone = "".join(
            list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath('//*[@itemprop="telephone"]//text()')
                    ],
                )
            )
        ).strip()

        location_type = "<MISSING>"

        hours = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath('//*[@itemprop="openingHours"]//text()')
                ],
            )
        )

        hours_of_operation = "; ".join(hours).replace("day;", "day:")

        latitude = store_res.text.split('"latitude":')[1].split(",")[0].strip()
        longitude = (
            store_res.text.split('"longitude":')[1]
            .split(",")[0]
            .strip()
            .replace("}", "")
            .strip()
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
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
