# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import urllib.parse

website = "coconutkennys.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


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


headers = {
    "authority": "www.coconutkennys.com",
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


def fetch_data():
    # Your scraper here
    search_url = "https://www.coconutkennys.com/locations/"
    with SgRequests(dont_retry_status_codes=([404])) as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//div[@class="et_pb_text_inner" and (./h3)]')
        for store in stores:
            page_url = search_url
            locator_domain = website
            location_name = "".join(store.xpath("h3//text()")).strip()
            map_link = "".join(store.xpath(".//a/@href")).strip()
            if "/menu/" in map_link:
                break
            raw_address = ""
            if "!2s" in map_link:
                raw_address = map_link.split("!2s")[1].strip().split("!3b")[0].strip()
            else:
                raw_address = (
                    map_link.split("/maps/place/")[1].strip().split("/")[0].strip()
                )

            raw_address = urllib.parse.unquote(raw_address.replace("+", " ")).split(",")
            street_address = ", ".join(raw_address[:-2]).strip()
            city = raw_address[-2]
            state = raw_address[-1].strip().split(" ")[0].strip()
            zip = raw_address[-1].strip().split(" ")[-1].strip()
            country_code = "US"

            store_number = "<MISSING>"
            phone = "".join(
                store.xpath(
                    'p/span[contains(text(),"CALL")]/following-sibling::span[1]/text()'
                )
            ).strip()
            if len(phone) <= 0:
                phone = "".join(
                    store.xpath(
                        'p/span[./span[contains(text(),"CALL")]]/following-sibling::span[1]/text()'
                    )
                ).strip()
            location_type = "<MISSING>"

            hours_of_operation = "".join(
                store.xpath(
                    'p/span[contains(text(),"HOURS")]/following-sibling::span[1]/text()'
                )
            ).strip()
            if len(hours_of_operation) <= 0:
                hours_of_operation = "".join(
                    store.xpath(
                        'p/span[./span[contains(text(),"HOURS")]]/following-sibling::span[1]/text()'
                    )
                ).strip()

            if len(hours_of_operation) <= 0:
                hours_of_operation = "11AM-9PM Monday to Sunday"

            latitude, longitude = get_latlng(map_link)

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
