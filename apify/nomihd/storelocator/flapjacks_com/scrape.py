# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "flapjacks.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "flapjacks.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
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
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here
    search_url = "https://flapjacks.com/locations/"
    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)

        store_list = search_sel.xpath(
            '//div[@class="wpb_column vc_column_container vc_col-sm-4"]'
        ) + search_sel.xpath(
            '//div[@class="wpb_column vc_column_container vc_col-sm-3"]'
        )

        for store in store_list:

            locator_domain = website

            location_name = "".join(store.xpath(".//p[1]//text()")).strip()
            if len(location_name) <= 0:
                continue
            store_info = store.xpath(".//p[2]/text()")
            phone = "<MISSING>"
            index = 0
            for info in store_info:
                index = index + 1
                if info.count("-") == 2:
                    phone = "".join(info).strip()
                    break

            full_address = store_info[: index - 2]
            street_address = ", ".join(full_address[:-1]).strip()
            city_state_zip = (
                full_address[-1]
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", " ")
                .strip()
            )
            city = city_state_zip.split(",")[0].strip()
            state = city_state_zip.split(",")[-1].strip().split(" ")[0].strip()
            zip = city_state_zip.split(",")[-1].strip().split(" ")[-1].strip()
            country_code = "US"

            store_number = "<MISSING>"

            location_type = "<MISSING>"

            hours_of_operation = "open weekdays from 8am to 1:00pm"

            map_link = "".join(store.xpath(".//a/@href"))

            latitude, longitude = get_latlng(map_link)
            page_url = "".join(store.xpath('.//a[@itemprop="url"]/@href')).strip()
            if page_url:
                page_url = "https://flapjacks.com" + page_url
                log.info(page_url)
                store_req = session.get(page_url, headers=headers)
                store_sel = lxml.html.fromstring(store_req.text)
                map_link = "".join(
                    store_sel.xpath('//iframe[contains(@src,"/maps/embed")]/@src')
                ).strip()
                latitude, longitude = get_latlng(map_link)
            else:
                page_url = search_url

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
