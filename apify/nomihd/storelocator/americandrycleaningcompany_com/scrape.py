# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "americandrycleaningcompany.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "www.americandrycleaningcompany.com",
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


data = {
    "store_locatore_search_input": " London, United Kingdom",
    "store_locatore_search_lat": "51.5073509",
    "store_locatore_search_lng": "-0.1277583",
    "store_locatore_search_radius": "5000",
    "store_locator_category": "",
    "map_id": "397",
    "action": "make_search_request_custom_maps",
    "lat": "51.5073509",
    "lng": "-0.1277583",
}


def fetch_data():
    # Your scraper here
    search_url = "https://www.americandrycleaningcompany.com/wp-admin/admin-ajax.php"
    search_res = session.post(search_url, headers=headers, data=data)

    search_sel = lxml.html.fromstring(search_res.text)
    store_list = search_sel.xpath('//div[contains(@class,"store-locator-item ")]')

    for store in store_list:
        page_url = store.xpath("./div/div/a[1]/@href")[0].strip()

        locator_domain = website

        log.info(page_url)
        store_res = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_res.text)

        raw_address = "<MISSING>"

        street_address = " ".join(
            store.xpath('.//div[@class="wpsl-address"]//text()')
        ).strip()
        city = (
            " ".join(store.xpath('.//div[@class="wpsl-city"]//text()'))
            .strip()
            .split(",")[0]
            .strip()
        )
        state = "<MISSING>"
        zip = (
            " ".join(store.xpath('.//div[@class="wpsl-city"]//text()'))
            .strip()
            .split(",")[1]
            .strip()
        )
        country_code = "GB"
        location_name = "".join(
            store.xpath('.//div[@class="wpsl-name"]//text()')
        ).strip()

        phone = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store.xpath(
                        './/a[contains(@href,"tel:")]//text() | .//tr[td="Phone"]/td[2]/text()'
                    )
                ],
            )
        )
        phone = " ".join(phone[:1]).strip()
        store_number = "".join(store.xpath("./@data-store-id")).strip('" ').strip()
        location_type = "<MISSING>"

        hours = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath(
                        '//div[contains(.//text(),"OPENING TIMES")]/following-sibling::div[table]//text()'
                    )
                ],
            )
        )
        hours_of_operation = (
            "; ".join(hours)
            .replace("Office Hours", "")
            .strip()
            .replace("Sat;", "Sat:")
            .replace("Sun;", "Sun:")
            .replace("day;", "day:")
            .replace("Thur;", "Thur:")
            .replace("Thurs;", "Thurs:")
            .replace("Fri;", "Fri:")
        )
        map_link = (
            "".join(store.xpath(".//a[@data-direction]/@data-direction"))
            .strip('" ')
            .strip()
        )

        latitude, longitude = (
            map_link.split(",")[0].strip(),
            map_link.split(",")[1].strip(),
        )

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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
