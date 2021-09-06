# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "actionurgentcare.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "actionurgentcare.com",
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


def get_latlng(map_link):
    if "z/data" in map_link:
        lat_lng = map_link.split("@")[1].split("z/data")[0]
        latitude = lat_lng.split(",")[0].strip()
        longitude = lat_lng.split(",")[1].strip()
    elif "ll=" in map_link:
        lat_lng = map_link.split("ll=")[1].split("&")[0]
        latitude = lat_lng.split(",")[0]
        longitude = lat_lng.split(",")[1]
    elif "!2d" in map_link and "!3d" in map_link:
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
    elif "/@" in map_link:
        latitude = map_link.split("/@")[1].split(",")[0].strip()
        longitude = map_link.split("/@")[1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here
    base = "http://actionurgentcare.com"
    search_url = "https://actionurgentcare.com/#locations"
    search_res = session.get(search_url, headers=headers)

    search_sel = lxml.html.fromstring(search_res.text)

    store_list = search_sel.xpath('//ul[@id="menu-locations-menu"]/li/a')

    for store in store_list:

        page_url = "".join(store.xpath("@href"))
        if "http" not in page_url:
            page_url = base + "/" + page_url
        locator_domain = website
        log.info(page_url)
        store_res = session.get(page_url, headers=headers)
        store_sel = lxml.html.fromstring(store_res.text)

        street_address = " ".join(
            store_sel.xpath('//span[@itemprop="streetAddress"]//text()')
        ).strip()
        city = " ".join(
            store_sel.xpath('//span[@itemprop="addressLocality"]//text()')
        ).strip()
        state = " ".join(
            store_sel.xpath('//span[@itemprop="addressRegion"]//text()')
        ).strip()
        zip = " ".join(
            store_sel.xpath('//span[@itemprop="postalCode"]//text()')
        ).strip()
        country_code = "US"

        location_name = "".join(store.xpath("text()")).strip()

        phone = " ".join(
            store_sel.xpath('//span[@itemprop="telephone"]//text()')
        ).strip()

        if len(street_address) <= 0:
            appoint_link = "".join(
                store_sel.xpath('//div[@class="app-container"]/iframe/@data-src')
            ).strip()
            temp_sel = lxml.html.fromstring(session.get(appoint_link).text)
            raw_info = temp_sel.xpath('//div[@class="address"]/text()')
            add_list = raw_info[0].split(",")
            street_address = ", ".join(add_list[:-2]).strip()
            city = add_list[-2].strip()
            state = add_list[-1].strip().split(" ")[0].strip()
            zip = add_list[-1].strip().split(" ")[-1].strip()
            phone = raw_info[-1].strip()

        store_number = "<MISSING>"

        location_type = "<MISSING>"
        hours = list(
            filter(
                str,
                [
                    x.strip()
                    for x in store_sel.xpath(
                        '//li[./i[contains(@class,"calendar")]]//text()'
                    )
                ],
            )
        )
        hours_of_operation = (
            "; ".join(hours).replace("Now Open!;", "").replace(":;", ":").strip()
        )
        if len(hours_of_operation) <= 0:
            hours_of_operation = "".join(
                store_sel.xpath('//div[@class="w-100"]/p/strong/text()')
            ).strip()

        map_link = "".join(
            store_sel.xpath('//iframe[contains(@data-src,"maps")]/@data-src')
        ).strip()

        latitude, longitude = get_latlng(map_link)

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
