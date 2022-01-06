# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "redwingheritage.jp"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
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
    search_url = "https://redwingheritage.jp/ext/stores.html"

    with SgRequests(dont_retry_status_codes=([404])) as session:
        stores_req = session.get(search_url, headers=headers)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath(
            '//div[@id="stores_tab_en"]/section[@class="p-stores-card"]'
        )

        for store in stores:
            locator_domain = website
            location_name = (
                " ".join(store.xpath(".//h2/text()")).strip().replace("\n", " ").strip()
            )
            page_url = "".join(
                store.xpath('.//a[contains(text(),"ABOUT STORE")]/@href')
            ).strip()

            store_number = page_url.split("?info_id=")[1].strip()

            location_type = "<MISSING>"

            street_address = (
                "".join(store.xpath('.//p[@class="p-stores-card__address"]/text()'))
                .strip()
                .replace(", Tokyo", "")
                .strip()
                .replace(", Osaka", "")
                .strip()
            )
            city = "".join(
                store.xpath('.//p[@class="p-stores-card__area"]/text()')
            ).strip()
            state = "<MISSING>"

            zip = "".join(
                store.xpath('.//span[@class="p-stores-card__postcode"]/text()')
            ).strip()

            country_code = "JP"

            phone = "".join(
                store.xpath('.//p[@class="p-stores-card__tel"]/text()')
            ).strip()

            hours = (
                "; ".join(store.xpath('.//div[@class="p-stores-card__info"]//text()'))
                .strip()
                .replace("Opening hour :", "")
                .strip()
                .replace("\n", "")
                .strip()
                .split(";")
            )
            hours_list = []
            for hour in hours:
                if len("".join(hour).strip()) > 0:
                    hours_list.append("".join(hour).strip())

            hours_of_operation = (
                "; ".join(hours_list)
                .strip()
                .replace("*Shortened business hours", "")
                .strip()
            )
            map_link = "".join(
                store.xpath('.//a[contains(text(),"MAP")]/@href')
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
