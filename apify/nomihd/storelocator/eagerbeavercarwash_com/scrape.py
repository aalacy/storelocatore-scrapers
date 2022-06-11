# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "eagerbeavercarwash.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "www.eagerbeavercarwash.com",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
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
    elif "/@" in map_link:
        latitude = map_link.split("/@")[1].split(",")[0].strip()
        longitude = map_link.split("/@")[1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here

    search_url = "https://www.eagerbeavercarwash.com/locations.html"

    with SgRequests(dont_retry_status_codes=([404])) as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)
        stores = search_sel.xpath(
            '//div[@class="row"][./div[@class="col-sm-4 col-centered text-center"]]'
        )
        for store in stores:
            page_url = search_url
            locator_domain = website

            location_name = "".join(
                store.xpath(
                    'div[@class="col-sm-4 col-centered text-center"]/div[@id="locheaders"]/text()'
                )
            ).strip()

            store_info = store.xpath(
                'div[@class="col-sm-4 col-centered text-center"]/text()'
            )
            raw_list = []
            for info in store_info:
                if len("".join(info).strip()) > 0:
                    raw_list.append("".join(info).strip())

            street_address = raw_list[0].strip()
            city = raw_list[1].strip().split(",")[0].strip()
            state = raw_list[1].strip().split(",")[-1].strip().split(" ")[0].strip()
            zip = raw_list[1].strip().split(",")[-1].strip().split(" ")[-1].strip()
            country_code = "US"
            store_number = location_name.split("#")[1].strip().split(")")[0].strip()

            phone = raw_list[2].strip().replace(":", "").strip()
            location_type = "".join(
                store.xpath(
                    'div[@class="col-sm-4 col-centered text-center"]//b[1]/text()'
                )
            ).strip()
            hours_of_operation = (
                "; ".join(raw_list[4:])
                .strip()
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "-")
                .strip()
            )

            map_link = "".join(
                store.xpath('.//iframe[contains(@src,"maps/embed?")]/@src')
            ).strip()

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
