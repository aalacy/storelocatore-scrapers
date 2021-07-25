# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "https://lhcgroup.com/#homecall"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "lhcgroup.com",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "origin": "https://lhcgroup.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://lhcgroup.com/locations/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_data():
    # Your scraper here
    search_url = "https://lhcgroup.com/wp-admin/admin-ajax.php"
    data = {
        "action": "search_locations",
        "q": "",
        "zip": "",
        "city": "",
        "state": "",
        "services": "",
        "family": "",
    }

    stores_req = session.post(search_url, data=data, headers=headers)
    raw_data = (
        json.loads(stores_req.text)["markup"]
        .replace('\\"', '"')
        .replace("\\/", "/")
        .strip()
    )
    stores_sel = lxml.html.fromstring(raw_data)
    stores = stores_sel.xpath('//article[@class="location-info-card"]')

    for store in stores:
        page_url = "".join(
            store.xpath('.//a[contains(text(),"Go to Page")]/@href')
        ).strip()
        log.info(page_url)
        store_req = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_req.text.replace("xlink:href", "href"))
        locator_domain = website

        location_name = "".join(
            store.xpath(
                ".//div[@class='info-card-contact-info']/div[@class='h5 alt']/text()"
            )
        ).strip()

        raw_list = []
        raw_info = store_sel.xpath(
            '//div[@class="info-item small"][.//use[contains(@href,"#icon_address")]]/div//text()'
        )
        for index in range(0, len(raw_info)):
            if len("".join(raw_info[index]).strip()) > 0:
                raw_list.append("".join(raw_info[index]).strip())

        street_address = "".join(
            store_sel.xpath(
                '//div[@itemprop="address"]/meta[@itemprop="streetAddress"]/@content'
            )
        ).strip()
        city = "".join(
            store_sel.xpath(
                '//div[@itemprop="address"]/meta[@itemprop="addressLocality"]/@content'
            )
        ).strip()
        state = "".join(
            store_sel.xpath(
                '//div[@itemprop="address"]/meta[@itemprop="addressRegion"]/@content'
            )
        ).strip()
        zip = "<MISSING>"
        if len(raw_list) > 0:
            zip = raw_list[-1]

        country_code = "US"

        store_number = "".join(store.xpath("@data-postid")).strip()

        phone = "".join(store_sel.xpath('//a[contains(@href,"tel:")]/text()')).strip()
        if len(phone) <= 0:
            phone = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//div[@class="info-item small"][.//use[contains(@href,"#icon_phone")]]/div/text()'
                        )
                    ],
                )
            )

            if len(phone) > 0:
                phone = "".join(phone[0]).strip()

        location_type = ""

        hours = store_sel.xpath(
            '//div[@class="info-item small"][.//use[contains(@href,"#icon_hours")]]'
        )
        hours_of_operation = "<MISSING>"
        if len(hours) > 0:
            hours_of_operation = (
                "; ".join("".join(hours[0].xpath("div/text()")).strip().split("\n"))
                .strip()
                .replace("\r", "")
                .strip()
            )

        latitude = "".join(store.xpath("@data-lat")).strip()
        longitude = "".join(store.xpath("@data-lng")).strip()

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
