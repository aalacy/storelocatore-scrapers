# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "waynescoffee.jo"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.waynescoffee.jo",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}


def get_store_data(session, _city, store_sel, page_url):
    locator_domain = website
    location_name = " ".join(
        store_sel.xpath("//h1[@class='single-cafe__title']/span[1]/text()")
    ).strip()
    raw_address = list(
        filter(
            str,
            store_sel.xpath('//h1[@class="single-cafe__title"]/span[2]/text()'),
        )
    )

    street_address = "".join(raw_address).strip()
    city = _city
    state = "<MISSING>"
    zip = "<MISSING>"
    country_code = "JO"

    store_number = "".join(
        store_sel.xpath('//ul[@id="cafe-opening-hours-list"]/@data-storeid')
    ).strip()
    phone = "".join(store_sel.xpath('//a[@class="link_phone"]/text()')).strip()

    location_type = "<MISSING>"
    hours_req = session.get(
        f"https://www.waynescoffee.jo/theme/ajax.php?action=cafe_opening&storeid={store_number}",
        headers=headers,
    )
    hours_sel = lxml.html.fromstring(hours_req.json()["data"])
    hours = hours_sel.xpath("//li")
    hours_list = []
    for hour in hours:
        day = "".join(hour.xpath('.//span[@class="opening-hours__day"]/text()')).strip()
        time = "".join(
            hour.xpath('.//span[@class="opening-hours__time"]/text()')
        ).strip()
        if not time:
            time = "".join(hour.xpath("p[2]/text()")).strip()

        hours_list.append(day + ":" + time)

    hours_of_operation = "; ".join(hours_list).strip()

    map_link = "".join(store_sel.xpath('//div[@id="cafe_map"]/@rel')).strip()
    latitude, longitude = (
        map_link.split(",")[0].strip(),
        map_link.split(",")[-1].strip(),
    )

    return SgRecord(
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
        raw_address=", ".join(raw_address).strip(),
    )


def fetch_data():
    # Your scraper here
    search_url = "http://www.waynescoffee.jo/cafes/"
    with SgRequests() as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//ul[@id="map-items"]/li')
        for store in stores:

            page_url = "".join(store.xpath("a/@href")).strip()
            _city = "".join(store.xpath("a/text()")).strip()
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            location_name = " ".join(
                store_sel.xpath("//h1[@class='single-cafe__title']/span[1]/text()")
            ).strip()
            if not location_name:
                sub_stores = store_sel.xpath('//ul[@class="cafe-items"]/li/a/@href')
                for sub_url in sub_stores:
                    log.info(sub_url)
                    sub_store_req = session.get(sub_url, headers=headers)
                    sub_store_sel = lxml.html.fromstring(sub_store_req.text)
                    yield get_store_data(session, _city, sub_store_sel, sub_url)
            else:
                yield get_store_data(session, _city, store_sel, page_url)


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
