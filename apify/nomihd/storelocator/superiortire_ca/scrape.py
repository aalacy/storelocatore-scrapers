# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "superiortire.ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.superiortire.ca",
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
    search_url = "https://www.superiortire.ca/Locations"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = list(
        search_sel.xpath('//div[contains(@class,"loc-widget") and not(./h2)]/div')
    )

    for store in store_list:

        page_url = "".join(store.xpath('.//a[contains(@href,"/Mode/")]/@href'))
        locator_domain = website

        location_name = "".join(
            search_sel.xpath(
                f'//*[@class="subtitle"][./a[@href="{page_url}"]]/strong//text()'
            )
        )

        street_address = ", ".join(
            store.xpath('.//div[contains(@class,"addr")]//text()')
        ).strip()
        if "," == street_address[-1]:
            street_address = "".join(street_address[:-1]).strip()

        csz = "".join(store.xpath('.//div[contains(@class,"csz")]//text()'))

        city = csz.split(",")[0].strip()

        state = csz.split(",")[1].strip().split(" ")[0].strip()
        zip = "".join(store.xpath('.//div[contains(@class,"zip")]//text()')).strip()

        country_code = "CA"

        store_number = page_url.split("Mode/")[1].split("/")[0].strip()
        phone = "".join(
            list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store.xpath(
                            './/div[contains(@class,"phone")]/a//text()'
                        )
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
                    for x in search_sel.xpath(
                        f'//*[@class="loccontact"][./a[@href="{page_url}"]]/div[@class="locationhours"]//text()'
                    )
                ],
            )
        )
        hours = hours[1:]
        hours_of_operation = "; ".join(hours).replace(":;", ":").strip()

        map_link = "".join(store.xpath('.//div[contains(@class,"latlong")]//text()'))

        if map_link:

            latitude, longitude = map_link.split(",")[0], map_link.split(",")[1]
        else:
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
