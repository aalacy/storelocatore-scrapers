# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "ikea.com/sa"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "ikea.com",
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
    search_url = "https://www.ikea.com/sa/en/stores/"
    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)
        store_list = search_sel.xpath('//div[@data-pub-type="page-list"]/div/div')
        log.info(len(store_list))
        for store in store_list:
            location_name = "".join(store.xpath(".//h2/text()")).strip()
            if (
                "collection point" in location_name.lower()
                or "planning studio" in location_name.lower()
            ):
                continue

            page_url = store.xpath(".//@href")[0].strip()

            locator_domain = website

            log.info(page_url)
            store_res = session.get(page_url, headers=headers)
            store_sel = lxml.html.fromstring(store_res.text)

            store_info = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//div[@data-pub-type="container"]//div[@data-pub-type="text"]/p[1]//text()'
                        )
                    ],
                )
            )

            raw_address = (
                " ".join(store_info).replace("IKEA", "").replace("Address:", "").strip()
            )
            if raw_address[0] == ",":
                raw_address = "".join(raw_address[1:]).strip()

            street_address = raw_address.split(",")[0].strip()
            city = raw_address.split(",")[1].strip().split(" ")[0].strip()
            state = "<MISSING>"
            try:
                zip = raw_address.split(",")[1].strip().split(" ")[1].strip()
            except:
                zip = "<MISSING>"

            country_code = "SA"

            location_name = "".join(store.xpath(".//h2/text()")).strip()

            phone = "<MISSING>"
            store_number = "<MISSING>"
            location_type = "<MISSING>"
            hours = list(
                filter(
                    str,
                    [
                        x.strip()
                        for x in store_sel.xpath(
                            '//div[@data-pub-type="container"]//div[@data-pub-type="text"]//p[contains(./strong/text(),"Store")]//text() | //div[@data-pub-type="container"]//div[@data-pub-type="text"]//p[contains(./strong/text(),"Store")]/following-sibling::p[1]//text()'
                        )
                    ],
                )
            )

            hours_of_operation = "; ".join(hours[1:]).replace("day;", "day:")

            map_link = "".join(store_sel.xpath('//a[contains(@href,"/maps")]/@href'))
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
