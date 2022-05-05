# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "gerbercollision.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Referer": "https://www.gerbercollision.com/",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.gerbercollision.com/locations"
    base = "https://www.gerbercollision.com"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    states = search_sel.xpath(
        '//div[@class="locations"]//div[@class="col-xs-4"]/a/@href'
    )
    for state in states:
        state_url = base + state
        stores_req = session.get(state_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        pagination = stores_sel.xpath('//div[@class="pagination"]//ul/li')
        if len(pagination) <= 0:
            pagination = ["Dummy"]
        for index in range(0, len(pagination)):
            if index > 0:
                stores_req = session.get(
                    state_url + "?n=" + str(index + 1), headers=headers
                )
                stores_sel = lxml.html.fromstring(stores_req.text)

            stores = stores_sel.xpath('//div[@class="row result"]')
            for store in stores:
                page_url = (
                    base
                    + "".join(
                        store.xpath(
                            './/div[@class="col-md-9 col-sm-6 data"]/h2/a/@href'
                        )
                    ).strip()
                )
                locator_domain = website

                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)

                location_name = "".join(
                    store_sel.xpath(
                        '//div[@class="location-info"]/div[@itemprop="name"]/text()'
                    )
                ).strip()
                if len(location_name) <= 0:
                    log.info("NO  NAAAAAMEE")

                    page_url = (
                        "https://www.boydautobody.com"
                        + "".join(
                            store.xpath(
                                './/div[@class="col-md-9 col-sm-6 data"]/h2/a/@href'
                            )
                        ).strip()
                    )
                    log.info(page_url)
                    store_req = session.get(page_url, headers=headers)
                    store_sel = lxml.html.fromstring(store_req.text)

                    location_name = "".join(
                        store_sel.xpath(
                            '//div[@class="location-info"]/div[@itemprop="name"]/text()'
                        )
                    ).strip()
                    if len(location_name) <= 0:
                        log.info("NO  NAAAAAMEE2222222")

                street_address = "".join(
                    store_sel.xpath(
                        '//div[@class="location-info"]//span[@itemprop="streetAddress"]/text()'
                    )
                ).strip()
                if len(street_address) > 0 and street_address[-1] == ",":
                    street_address = "".join(street_address[:-1]).strip()

                city = "".join(
                    store_sel.xpath(
                        '//div[@class="location-info"]//span[@itemprop="addressLocality"]/text()'
                    )
                ).strip()
                state = "".join(
                    store_sel.xpath(
                        '//div[@class="location-info"]//span[@itemprop="addressRegion"]/text()'
                    )
                ).strip()
                zip = "".join(
                    store_sel.xpath(
                        '//div[@class="location-info"]//span[@itemprop="postalCode"]/text()'
                    )
                ).strip()
                country_code = "US"
                if " " in zip:
                    country_code = "CA"

                store_number = "<MISSING>"
                phone = "".join(
                    store_sel.xpath(
                        '//div[@class="location-info"]//span[@itemprop="telephone"]/text()'
                    )
                ).strip()
                if len(phone) <= 0:
                    continue

                location_type = "<MISSING>"

                hours = store_sel.xpath(
                    '//div[@class="location-info"]//p[@itemprop="openingHours"]'
                )
                hours_list = []
                for hour in hours:
                    day = "".join(hour.xpath("text()")).strip()
                    time = "".join(hour.xpath("strong/text()")).strip()
                    hours_list.append(day + ": " + time)

                if len(hours_list) <= 0:
                    hours_list = store_sel.xpath(
                        '//div[@class="location-info"]//div[@class="timesheet"]/text()'
                    )
                hours_of_operation = (
                    "; ".join(hours_list)
                    .strip()
                    .replace("\n", "")
                    .strip()
                    .replace("day;", "day:")
                    .strip()
                )
                if len(hours_of_operation) > 0 and hours_of_operation[0] == ";":
                    hours_of_operation = "".join(hours_of_operation[1:]).strip()

                latitude = "".join(
                    store.xpath('.//div[@class="location-map2"]/@data-lat')
                ).strip()
                longitude = "".join(
                    store.xpath('.//div[@class="location-map2"]/@data-lng')
                ).strip()

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
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STATE,
                    SgRecord.Headers.ZIP,
                }
            )
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
