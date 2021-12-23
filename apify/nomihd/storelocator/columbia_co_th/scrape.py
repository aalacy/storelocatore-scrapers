# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "columbia.co.th"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "columbia.co.th",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "referer": "https://columbia.co.th/store",
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
    elif "&q=" in map_link:
        latitude = map_link.split("&q=")[1].split(",")[0].strip()
        longitude = map_link.split("&q=")[1].split(",")[1].strip()
    elif "?q=" in map_link:
        latitude = map_link.split("?q=")[1].split(",")[0].strip()
        longitude = map_link.split("?q=")[1].split(",")[1].strip().split("&")[0].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    # Your scraper here

    with SgRequests(dont_retry_status_codes=([404])) as session:
        search_res = session.get("https://columbia.co.th/store", headers=headers)
        search_sel = lxml.html.fromstring(search_res.text)
        stores = search_sel.xpath('//div[@class="store-location-card"]')

        for store in stores:

            page_url = (
                "https://columbia.co.th/" + "".join(store.xpath("a/@href")).strip()
            )
            log.info(page_url)
            store_req = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_req.text)

            locator_domain = website

            location_name = "".join(
                store.xpath('.//p[@class="store-name"]/text()')
            ).strip()

            temp_address = store_sel.xpath(
                '//section[@class="cb-section"]//div[@class="col-12 col-sm-6"][1]/p'
            )[:-1]
            add_list = []
            for temp in temp_address:
                add_chunk = temp.xpath("big/text()")
                for chunk in add_chunk:
                    if len("".join(chunk).strip()) > 0:
                        add_list.append("".join(chunk).strip())

            street_address = ", ".join(add_list[:-1]).strip()

            city = add_list[-1].strip().rsplit(" ", 1)[0].strip()
            state = street_address.rsplit(" ")[-1].strip()
            street_address = street_address.replace(state, "").strip()

            zip = add_list[-1].strip().rsplit(" ", 1)[-1].strip()

            country_code = "TH"

            store_number = page_url.split("/")[-1].strip()

            phone = (
                "".join(
                    store_sel.xpath(
                        '//section[@class="cb-section"]//div[@class="col-12 col-sm-6"][1]/p'
                    )[-1].xpath("big/text()")
                )
                .strip()
                .split(".")[-1]
                .strip()
            )

            location_type = "<MISSING>"
            hours_of_operation = (
                "".join(store.xpath('.//p[@class="store-operate-time"]/text()'))
                .strip()
                .replace("Time open", "")
                .strip()
                .encode("ascii", "replace")
                .decode("utf-8")
                .replace("?", "@")
                .strip()
                .split("@")[0]
                .strip()
            )

            map_link = "".join(
                store_sel.xpath('//section[@class="cb-section"]//iframe/@src')
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
