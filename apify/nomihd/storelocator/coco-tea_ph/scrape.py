# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import lxml.html

website = "coco-tea.ph"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Referer": "https://coco-tea.ph/manila/",
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

    search_url = "https://coco-tea.ph/quezon-city/"
    with SgRequests() as session:
        search_req = session.get(search_url, headers)
        search_sel = lxml.html.fromstring(search_req.text)
        cities = search_sel.xpath(
            '//div[@class="uk-panel desktop-store-location widget-menu"]//li/a'
        ) + search_sel.xpath('//li/a[@class="el-link"]')
        for cit in cities:
            city_url = "".join(cit.xpath("@href")).strip()
            if "#" in city_url:
                continue

            if "http" not in city_url:
                city_url = "https://coco-tea.ph" + city_url

            log.info(city_url)
            stores_req = session.get(city_url, headers=headers)
            stores_sel = lxml.html.fromstring(stores_req.text)
            stores = stores_sel.xpath(
                '//article/div/div[@class="uk-margin-large-bottom"]'
            )
            for store in stores:
                page_url = city_url
                location_name = " ".join(
                    store.xpath("h3[@class='wk-panel-title']/text()")
                ).strip()
                # if "Opening Soon" in location_name:
                #     continue
                locator_domain = website

                raw_info = store.xpath("p[1]/text()")
                raw_info_list = []
                for raw in raw_info:
                    if len("".join(raw).strip()) > 0:
                        raw_info_list.append("".join(raw).strip())

                hours_of_operation = ""
                raw_address = ""
                for index in range(0, len(raw_info_list)):
                    if (
                        "Monday" in raw_info_list[index]
                        or "Sunday" in raw_info_list[index]
                        or "Temporarily Closed" in raw_info_list[index]
                    ):
                        hours_of_operation = "; ".join(raw_info_list[index:]).strip()
                        raw_address = ", ".join(raw_info_list[:index]).strip()
                        break

                if raw_address == "":
                    raw_address = ", ".join(raw_info_list).strip()

                street_address = ", ".join(raw_address.split(",")[:-1]).strip()
                city = raw_address.split(",")[-1].strip()

                state = "<MISSING>"
                zip = "<MISSING>"
                country_code = "PH"

                phone = "<MISSING>"
                store_number = "<MISSING>"
                location_type = "<MISSING>"
                map_link = "".join(store.xpath("p/iframe/@src")).strip()
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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.CITY,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
