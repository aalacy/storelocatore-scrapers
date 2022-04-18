# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "derrels.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.derrels.com",
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def fetch_store_urls(stores_sel, session):
    stores = stores_sel.xpath(
        '//div[@class="menu-tab-item city city four-column"][./div[@class="count"]]'
    )
    store_urls_list = []
    for store in stores:
        if "".join(store.xpath('div[@class="count"]/span/text()')).strip() == "1":
            temp_url = (
                "https://www.derrels.com"
                + "".join(
                    store.xpath('a[contains(@href,"/storage-units/california/")]/@href')
                ).strip()
            )
            store_urls_list.append(temp_url)
        else:
            temp_url = (
                "https://www.derrels.com"
                + "".join(
                    store.xpath('a[contains(@href,"/storage-units/california/")]/@href')
                ).strip()
            )

            temp_stores_req = session.get(temp_url, headers=headers)
            temp_stores_sel = lxml.html.fromstring(temp_stores_req.text)
            store_urls = temp_stores_sel.xpath(
                '//div[@class="location-container"]//div[@class="title"]/a/@href'
            )
            for url in store_urls:
                store_urls_list.append("https://www.derrels.com" + url)

    return store_urls_list


def fetch_data():
    # Your scraper here
    search_url = "https://www.derrels.com/storage-units/locations/"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        store_urls_list = fetch_store_urls(stores_sel, session)
        for store_url in list(set(store_urls_list)):
            page_url = store_url
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)
            locator_domain = website
            store_json = json.loads(
                "".join(
                    store_sel.xpath('//script[@type="application/ld+json"]/text()')
                ).strip()
            )

            location_name = "".join(
                store_sel.xpath('//div[@class="facility-info"]/h2/text()')
            ).strip()

            street_address = ""
            city = ""
            state = ""
            zip = ""
            latitude = ""
            longitude = ""

            for js in store_json:
                if js["@type"] == "SelfStorage":
                    street_address = js["address"]["streetAddress"]
                    city = js["address"]["addressLocality"]
                    state = js["address"]["addressRegion"]
                    zip = js["address"]["postalCode"]
                    latitude = js["geo"]["latitude"]
                    longitude = js["geo"]["longitude"]
                    break

            country_code = "US"

            store_number = "<MISSING>"
            phone = "".join(store_sel.xpath('//a[@class="phone bold"]/text()')).strip()
            location_type = "<MISSING>"

            hours = store_sel.xpath('//div[@class="office-hours"]/div')
            hours_list = []
            for hour in hours:
                day = "".join(hour.xpath("div[1]/text()")).strip()
                time = "".join(hour.xpath("div[2]/text()")).strip()
                hours_list.append(day + ": " + time)

            hours_of_operation = "; ".join(hours_list).strip()

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
